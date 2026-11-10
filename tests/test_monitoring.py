import asyncio
import json
import logging
import re
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from importlib import import_module
from pathlib import Path
from uuid import UUID

import pytest
from starlette.testclient import TestClient

from careerpath import service

PROFILE = {
    "age": 35,
    "education": "Bachelors",
    "workclass": "Private",
    "occupation": "Tech-support",
    "marital_status": "Never-married",
    "hours_per_week": 40,
}


def events(path: Path) -> list[dict]:
    assert path.is_file(), "the HTTP service must create its append-only inference log"
    return [json.loads(line) for line in path.read_text("utf-8").splitlines()]


@pytest.fixture
def inference_log(tmp_path, monkeypatch):
    path = tmp_path / "logs" / "inference.jsonl"
    monkeypatch.setenv("CAREERPATH_LOG_PATH", str(path))
    return path


@pytest.fixture
def client(service_app, inference_log):
    with TestClient(service_app) as test_client:
        yield test_client


def test_success_records_input_response_and_operation(client, inference_log):
    response = client.post("/predict", json=PROFILE)
    assert response.status_code == 200
    [event] = events(inference_log)
    assert event["schema_version"] == 1
    assert event["input"] == PROFILE
    assert event["output"] == response.json()
    assert event["model_version"] == "adult-income-v1"
    assert (event["method"], event["endpoint"], event["status_code"]) == ("POST", "/predict", 200)
    assert event["outcome"] == "success"
    assert event["input_capture"] == "complete"
    assert event["error_type"] is None
    assert 0 <= event["output"]["probability_above_50k"] <= 1
    assert event["latency_ms"] >= 0
    assert UUID(event["request_id"]).version == 4
    assert re.fullmatch(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d\.\d{6}\+00:00", event["timestamp"])
    assert datetime.fromisoformat(event["timestamp"]).utcoffset().total_seconds() == 0


def test_append_survives_lifespan_restart_and_reconfiguration(service_app, inference_log):
    inference_log.parent.mkdir(parents=True)
    prefix = b'{"previous":true}\n'
    inference_log.write_bytes(prefix)
    for _ in range(2):
        with TestClient(service_app) as client:
            monitoring = import_module("careerpath.monitoring")
            monitoring.configure_monitoring(inference_log)
            monitoring.configure_monitoring(inference_log)
            assert client.post("/predict", json=PROFILE).status_code == 200
        assert inference_log.read_bytes().startswith(prefix)
        prefix = inference_log.read_bytes()
    recorded = events(inference_log)
    assert len(recorded) == 3
    assert recorded[0] == {"previous": True}
    assert len({e["request_id"] for e in recorded[1:]}) == 2


@pytest.mark.parametrize(
    ("body", "capture"),
    [
        (b"{", "invalid_json"),
        (json.dumps({**PROFILE, "age": -1}).encode(), "complete"),
        (json.dumps({**PROFILE, "email": "hidden@example.test"}).encode(), "complete"),
        (b"[]", "unsupported"),
        (json.dumps({**PROFILE, "age": float("nan")}).encode(), "invalid_json"),
    ],
)
def test_rejections_are_logged_before_inference(client, inference_log, monkeypatch, body, capture):
    def unexpected_inference(*args):
        pytest.fail("invalid input reached inference")

    monkeypatch.setattr(service, "predict_income", unexpected_inference)
    assert client.post("/predict", content=body).status_code == 400
    [event] = events(inference_log)
    assert event["status_code"] == 400
    assert event["outcome"] == "client_error"
    assert event["error_type"] == "client_error"
    assert event["output"] is None
    assert event["input_capture"] == capture
    assert "hidden@example.test" not in inference_log.read_text("utf-8")


def test_nullable_and_unicode_unknown_categories_are_preserved(client, inference_log):
    profile = {**PROFILE, "workclass": None, "occupation": "Operação\nTécnica"}
    response = client.post("/predict", json=profile)
    assert response.status_code == 200
    [event] = events(inference_log)
    assert event["input"] == profile
    assert event["output"] == response.json()


def test_internal_error_does_not_leak_exception_or_fabricate_output(
    client,
    inference_log,
    monkeypatch,
):
    def fail(*args):
        raise RuntimeError("private-exception-detail")

    monkeypatch.setattr(service, "predict_income", fail)
    assert client.post("/predict", json=PROFILE).status_code == 500
    [event] = events(inference_log)
    assert event["outcome"] == event["error_type"] == "server_error"
    assert event["status_code"] == 500
    assert event["input"] == PROFILE
    assert event["output"] is None
    assert "private-exception-detail" not in inference_log.read_text("utf-8")


def test_health_is_not_an_inference_event(client, inference_log):
    assert client.get("/health").status_code == 200
    assert inference_log.read_bytes() == b""


def test_large_valid_body_still_predicts_but_marks_capture_truncated(client, inference_log):
    body = b" " * 8192 + json.dumps(PROFILE).encode()
    response = client.post("/predict", content=body)
    assert response.status_code == 200
    [event] = events(inference_log)
    assert event["input_capture"] == "truncated"
    assert event["input"] == {}
    assert event["output"] == response.json()


def test_metrics_passes_through_without_creating_an_event(tmp_path):
    monitoring = import_module("careerpath.monitoring")
    path = tmp_path / "events.jsonl"
    logger = monitoring.configure_monitoring(path)
    sent = []

    async def app(scope, receive, send):
        await send({"type": "http.response.start", "status": 200})
        await send({"type": "http.response.body", "body": b"metric_total 3\n"})

    async def receive():
        pytest.fail("metrics does not need an inference body")

    async def send(message):
        sent.append(message)

    asyncio.run(
        monitoring.InferenceLoggingMiddleware(app, logger=logger, model_version="v1")(
            {"type": "http", "path": "/metrics", "method": "GET"},
            receive,
            send,
        )
    )
    assert sent == [
        {"type": "http.response.start", "status": 200},
        {"type": "http.response.body", "body": b"metric_total 3\n"},
    ]
    assert path.read_bytes() == b""
    for handler in logger.handlers[:]:
        handler.close()
        logger.removeHandler(handler)


def test_partial_response_failure_is_logged_once_and_reraised(tmp_path):
    monitoring = import_module("careerpath.monitoring")
    path = tmp_path / "events.jsonl"
    logger = monitoring.configure_monitoring(path)
    sent = []

    async def app(scope, receive, send):
        await receive()
        await send({"type": "http.response.start", "status": 200})
        await send({"type": "http.response.body", "body": b"{", "more_body": True})
        raise RuntimeError("private-stream-detail")

    async def receive():
        return {"type": "http.request", "body": json.dumps(PROFILE).encode()}

    async def send(message):
        sent.append(message)

    try:
        with pytest.raises(RuntimeError, match="private-stream-detail"):
            middleware = monitoring.InferenceLoggingMiddleware(
                app, logger=logger, model_version="v1"
            )
            asyncio.run(
                middleware(
                    {"type": "http", "path": "/predict", "method": "POST"},
                    receive,
                    send,
                )
            )
        [event] = events(path)
        assert len(sent) == 2
        assert event["status_code"] == 200
        assert event["outcome"] == "server_error"
        assert event["input"] == PROFILE
        assert event["output"] is None
        assert "private-stream-detail" not in path.read_text("utf-8")
    finally:
        for handler in logger.handlers[:]:
            handler.close()
            logger.removeHandler(handler)


def test_concurrent_requests_keep_inputs_outputs_and_ids_separate(client, inference_log):
    def predict(age):
        response = client.post("/predict", json={**PROFILE, "age": age})
        assert response.status_code == 200
        return age, response.json()

    with ThreadPoolExecutor(max_workers=4) as pool:
        expected = dict(pool.map(predict, range(25, 37)))
    recorded = events(inference_log)
    assert len(recorded) == 12
    assert len({e["request_id"] for e in recorded}) == 12
    assert {e["input"]["age"]: e["output"] for e in recorded} == expected


def test_startup_propagates_open_failure(service_app, inference_log, monkeypatch):
    def denied(*args, **kwargs):
        raise PermissionError("destination is unavailable")

    monkeypatch.setattr(logging.FileHandler, "_open", denied)
    with pytest.raises(PermissionError, match="destination is unavailable"):
        with TestClient(service_app):
            pytest.fail("startup accepted an unavailable log destination")


def test_disk_failure_is_visible_even_when_logging_exceptions_are_disabled(
    client,
    inference_log,
    monkeypatch,
    capsys,
):
    class BrokenStream:
        def write(self, value):
            raise OSError("private-disk-detail")

        def flush(self):
            pass

        def close(self):
            pass

    monitoring = import_module("careerpath.monitoring")
    logger = monitoring.configure_monitoring(inference_log)
    handler = logger.handlers[0]
    old_stream = handler.setStream(BrokenStream())
    monkeypatch.setattr(logging, "raiseExceptions", False)
    try:
        response = client.post("/predict", json=PROFILE)
        assert response.status_code == 200
        assert response.json()["model_version"] == "adult-income-v1"
        error = capsys.readouterr().err
        assert "monitoring" in error.lower()
        assert "failed" in error.lower()
        assert "private-disk-detail" not in error
    finally:
        handler.setStream(old_stream)


def test_default_log_path_is_relative_to_process_directory(service_app, tmp_path, monkeypatch):
    monkeypatch.delenv("CAREERPATH_LOG_PATH", raising=False)
    monkeypatch.chdir(tmp_path)
    with TestClient(service_app) as client:
        assert client.post("/predict", json=PROFILE).status_code == 200
    assert len(events(tmp_path / "logs" / "inference.jsonl")) == 1


def test_raw_asgi_chunks_limits_and_allowlist(tmp_path):
    monitoring = import_module("careerpath.monitoring")
    path = tmp_path / "raw.jsonl"
    logger = monitoring.configure_monitoring(path)
    original_bodies = [
        json.dumps({"age": 35, "occupation": "Ação\n" + "x" * 100, "email": "hidden"}).encode(),
        json.dumps({**PROFILE, "occupation": {"secret": "hidden"}}).encode(),
        json.dumps({**PROFILE, "age": float("inf")}).encode(),
        json.dumps({**PROFILE, "extra": "x" * 9000}).encode(),
    ]

    async def exercise(body):
        chunks = [body[:7], body[7:19], body[19:]]
        messages = [
            {"type": "http.request", "body": chunk, "more_body": index < 2}
            for index, chunk in enumerate(chunks)
        ]
        response = (
            b'{"income_class_proxy":"<=50K","probability_above_50k":0.25,"model_version":"v1"}'
        )
        outgoing = [
            {"type": "http.response.start", "status": 200, "headers": []},
            {"type": "http.response.body", "body": response[:25], "more_body": True},
            {"type": "http.response.body", "body": response[25:]},
        ]
        sent = []

        async def receive():
            return messages.pop(0)

        async def send(message):
            sent.append(message)

        async def app(scope, receive, send):
            consumed = b""
            for _ in range(3):
                consumed += (await receive())["body"]
            assert consumed == body
            for message in outgoing:
                await send(message)

        middleware = monitoring.InferenceLoggingMiddleware(app, logger=logger, model_version="v1")
        await middleware(
            {"type": "http", "method": "POST", "path": "/predict", "headers": []},
            receive,
            send,
        )
        assert sent == outgoing

    try:
        for body in original_bodies:
            asyncio.run(exercise(body))
        recorded = events(path)
        assert recorded[0]["input"] == {"age": 35, "occupation": ("Ação\n" + "x" * 100)[:80]}
        assert "occupation" not in recorded[1]["input"]
        assert recorded[2]["input_capture"] == "invalid_json"
        assert recorded[3]["input_capture"] == "truncated"
        assert recorded[3]["input"] == {}
        assert all(e["output"]["probability_above_50k"] == 0.25 for e in recorded)
        assert "hidden" not in path.read_text("utf-8")
    finally:
        for handler in logger.handlers[:]:
            handler.close()
            logger.removeHandler(handler)
