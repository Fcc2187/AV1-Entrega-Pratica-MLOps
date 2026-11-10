"""Bounded HTTP capture and append-only inference events for one application worker."""

import json
import logging
import math
import sys
from datetime import UTC, datetime
from pathlib import Path
from time import perf_counter
from uuid import uuid4

from starlette.types import ASGIApp, Message, Receive, Scope, Send

_LOGGER = logging.getLogger(__name__)
_CAPTURE_BYTES = 8192
_INPUT_FIELDS = (
    "age",
    "education",
    "workclass",
    "occupation",
    "marital_status",
    "hours_per_week",
)
_OUTPUT_FIELDS = ("income_class_proxy", "probability_above_50k", "model_version")


def _report_write_failure() -> None:
    # Do not include payloads, filesystem errors or exception text in this fallback.
    print("CareerPath monitoring: failed to write inference event", file=sys.stderr)


class _InferenceFileHandler(logging.FileHandler):
    def handleError(self, record: logging.LogRecord) -> None:
        # Logging normally hides stream errors when logging.raiseExceptions is False.
        _report_write_failure()


def configure_monitoring(log_path: Path) -> logging.Logger:
    """Open the destination before accepting traffic; reconfiguration is idempotent."""
    destination = log_path.resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    for handler in _LOGGER.handlers:
        if (
            isinstance(handler, _InferenceFileHandler)
            and handler.baseFilename == str(destination)
            and handler.stream is not None
        ):
            return _LOGGER
    handler = _InferenceFileHandler(destination, mode="a", encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(message)s"))
    for previous in _LOGGER.handlers[:]:
        previous.close()
        _LOGGER.removeHandler(previous)
    _LOGGER.setLevel(logging.INFO)
    _LOGGER.propagate = False
    _LOGGER.addHandler(handler)
    return _LOGGER


def _reject_constant(value: str) -> None:
    raise ValueError("non-finite JSON constant")


class _BodyCapture:
    def __init__(self) -> None:
        self.data = bytearray()
        self.truncated = False
        self.complete = False

    def append(self, body: bytes, more: bool) -> None:
        available = _CAPTURE_BYTES - len(self.data)
        self.truncated |= len(body) > available
        self.data.extend(body[:available])
        self.complete = not more

    def decode(self) -> tuple[dict, str]:
        if self.truncated:
            return {}, "truncated"
        if not self.complete:
            return {}, "unsupported"
        try:
            value = json.loads(self.data, parse_constant=_reject_constant)
        except (ValueError, UnicodeError, RecursionError):
            return {}, "invalid_json"
        if not isinstance(value, dict):
            return {}, "unsupported"
        return value, "complete"


def _select_fields(data: dict, fields: tuple[str, ...]) -> dict:
    selected = {}
    for field in fields:
        if field not in data:
            continue
        value = data[field]
        if isinstance(value, str):
            selected[field] = value[:80]
        elif value is None or isinstance(value, (bool, int)):
            selected[field] = value
        elif isinstance(value, float) and math.isfinite(value):
            selected[field] = value
    return selected


class InferenceLoggingMiddleware:
    """Observe /predict without consuming, replacing or rejecting HTTP messages."""

    def __init__(self, app: ASGIApp, *, logger: logging.Logger, model_version: str) -> None:
        self.app = app
        self.logger = logger
        self.model_version = model_version

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http" or scope["path"] != "/predict":
            return await self.app(scope, receive, send)

        started = perf_counter()
        request_id = str(uuid4())
        incoming, outgoing = _BodyCapture(), _BodyCapture()
        status = None
        finished = None
        timestamp = None
        failed = False

        async def capture_receive() -> Message:
            message = await receive()
            if message["type"] == "http.request":
                incoming.append(message.get("body", b""), message.get("more_body", False))
            return message

        async def capture_send(message: Message) -> None:
            nonlocal status, finished, timestamp
            await send(message)
            if message["type"] == "http.response.start":
                status = message["status"]
            elif message["type"] == "http.response.body":
                outgoing.append(message.get("body", b""), message.get("more_body", False))
                if outgoing.complete:
                    finished = perf_counter()
                    timestamp = datetime.now(UTC)

        try:
            await self.app(scope, capture_receive, capture_send)
        except BaseException:
            failed = True
            raise
        finally:
            input_data, input_capture = incoming.decode()
            content_type = dict(scope.get("headers", [])).get(b"content-type", b"application/json")
            media_type = content_type.split(b";", 1)[0].strip().lower()
            if media_type != b"application/json" and not media_type.endswith(b"+json"):
                input_data, input_capture = {}, "unsupported"

            if failed or status is None or status >= 500 or not outgoing.complete:
                outcome = "server_error"
            elif status >= 400:
                outcome = "client_error"
            else:
                outcome = "success"
            output_data, output_capture = outgoing.decode()
            output = (
                _select_fields(output_data, _OUTPUT_FIELDS)
                if outcome == "success" and output_capture == "complete"
                else None
            )
            event = {
                "schema_version": 1,
                "timestamp": (timestamp or datetime.now(UTC)).isoformat(timespec="microseconds"),
                "request_id": request_id,
                "method": scope["method"],
                "endpoint": scope["path"],
                "status_code": status,
                "outcome": outcome,
                "latency_ms": ((finished if finished is not None else perf_counter()) - started)
                * 1000,
                "input": _select_fields(input_data, _INPUT_FIELDS),
                "input_capture": input_capture,
                "output": output,
                "model_version": self.model_version,
                "error_type": None if outcome == "success" else outcome,
            }
            try:
                self.logger.info(json.dumps(event, allow_nan=False))
            except Exception:
                _report_write_failure()
