import json
import math
import os
import shutil
import signal
import socket
import subprocess
import time
from pathlib import Path
from typing import IO
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from prometheus_client.parser import text_string_to_metric_families
from prometheus_client.samples import Sample

PROJECT_ROOT = Path(__file__).parents[1]


def free_port() -> int:
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        return listener.getsockname()[1]


def request_json(
    port: int, path: str, payload: dict[str, object] | None = None
) -> tuple[int, dict[str, object]]:
    data = json.dumps(payload).encode() if payload is not None else None
    request = Request(
        f"http://127.0.0.1:{port}{path}",
        data=data,
        headers={"content-type": "application/json"} if data else {},
        method="POST" if data else "GET",
    )
    try:
        response = urlopen(request, timeout=2)
    except HTTPError as error:
        response = error
    with response:
        return response.status, json.load(response)


def request_metrics(port: int) -> tuple[str, list[Sample]]:
    with urlopen(f"http://127.0.0.1:{port}/metrics", timeout=3) as response:
        assert response.status == 200
        assert response.headers.get_content_type() in ("text/plain", "application/openmetrics-text")
        text = response.read().decode("utf-8")
    families = list(text_string_to_metric_families(text))
    assert any(f.name == "bentoml_service_request" and f.type == "counter" for f in families)
    assert any(
        f.name == "bentoml_service_request_duration_seconds" and f.type == "histogram"
        for f in families
    )
    return text, [sample for family in families for sample in family.samples]


def metric_value(samples: list[Sample], name: str, **labels: str) -> float:
    return sum(
        sample.value
        for sample in samples
        if sample.name == name
        and sample.labels.get("endpoint") == "/predict"
        and all(sample.labels.get(key) == value for key, value in labels.items())
    )


def start_service(port: int, log: IO[str], inference_log: Path) -> subprocess.Popen[str]:
    uv = shutil.which("uv")
    assert uv is not None, "uv is required to run the documented service command"
    options: dict[str, object] = {
        "cwd": PROJECT_ROOT,
        "env": {
            **os.environ,
            "BENTOML_DO_NOT_TRACK": "True",
            "CAREERPATH_LOG_PATH": str(inference_log),
        },
        "stdout": log,
        "stderr": subprocess.STDOUT,
        "text": True,
    }
    if os.name == "nt":
        options["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
    else:
        options["start_new_session"] = True
    return subprocess.Popen(
        [
            uv,
            "run",
            "--frozen",
            "bentoml",
            "serve",
            "careerpath.service:CareerPathService",
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
            "--do-not-track",
        ],
        **options,
    )


def wait_for_port_closed(port: int) -> None:
    deadline = time.monotonic() + 5
    while time.monotonic() < deadline:
        with socket.socket() as probe:
            probe.settimeout(0.2)
            if probe.connect_ex(("127.0.0.1", port)) != 0:
                return
        time.sleep(0.05)
    raise AssertionError(f"service still listens on port {port} after shutdown")


def stop_service(process: subprocess.Popen[str], port: int) -> None:
    if os.name == "nt":
        if process.poll() is None:
            try:
                subprocess.run(
                    ["taskkill", "/PID", str(process.pid), "/T", "/F"],
                    check=False,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    timeout=10,
                )
            except subprocess.TimeoutExpired:
                process.kill()
    else:
        try:
            os.killpg(process.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
    try:
        process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        if os.name != "nt":
            os.killpg(process.pid, signal.SIGKILL)
        else:
            process.kill()
        process.wait(timeout=5)
    wait_for_port_closed(port)


def wait_for_health(
    process: subprocess.Popen[str], port: int, log: IO[str], log_path: Path
) -> dict[str, object]:
    deadline = time.monotonic() + 30
    while time.monotonic() < deadline:
        if process.poll() is not None:
            break
        try:
            status, body = request_json(port, "/health")
            if status == 200:
                return body
        except (ConnectionError, TimeoutError, URLError):
            pass
        time.sleep(0.1)
    log.flush()
    raise AssertionError(f"service did not become healthy:\n{log_path.read_text('utf-8')}")


def test_service_predicts_after_real_restart(tmp_path: Path) -> None:
    port = free_port()
    profile = {
        "age": 35,
        "education": "Bachelors",
        "workclass": "Private",
        "occupation": "Tech-support",
        "marital_status": "Never-married",
        "hours_per_week": 40,
    }

    inference_log = tmp_path / "inference.jsonl"
    measurements = []
    previous_log = b""
    previous_prediction = None
    request_ids: set[str] = set()
    for attempt in range(2):
        log_path = tmp_path / f"service-{attempt}.log"
        with log_path.open("w", encoding="utf-8") as log:
            process = start_service(port, log, inference_log)
            try:
                health = wait_for_health(process, port, log, log_path)
                assert inference_log.read_bytes() == previous_log
                before_text, before = request_metrics(port)
                # Each fresh process starts a new window, including after restart.
                assert metric_value(before, "bentoml_service_request_total") == 0
                status, prediction = request_json(port, "/predict", profile)
                invalid_status, _ = request_json(port, "/predict", {**profile, "age": -1})
                after_text, after = request_metrics(port)
            finally:
                stop_service(process, port)

        assert process.poll() is not None
        assert health == {"status": "ok", "model_version": "adult-income-v1"}
        assert status == 200
        assert prediction["income_class_proxy"] in {"<=50K", ">50K"}
        assert 0 <= prediction["probability_above_50k"] <= 1
        assert prediction["model_version"] == "adult-income-v1"
        if previous_prediction is not None:
            assert prediction == previous_prediction
        previous_prediction = prediction
        assert invalid_status == 400

        current_log = inference_log.read_bytes()
        assert current_log.startswith(previous_log)
        appended = current_log[len(previous_log) :].splitlines()
        assert len(appended) == 2
        accepted, rejected = (json.loads(line) for line in appended)
        assert (accepted["status_code"], rejected["status_code"]) == (200, 400)
        assert accepted["input"] == profile
        assert accepted["output"] == prediction
        assert rejected["input"]["age"] == -1
        assert rejected["output"] is None
        new_ids = {accepted["request_id"], rejected["request_id"]}
        assert len(new_ids) == 2 and request_ids.isdisjoint(new_ids)
        request_ids.update(new_ids)

        counter = "bentoml_service_request_total"
        duration = "bentoml_service_request_duration_seconds"
        counter_deltas = {
            code: metric_value(after, counter, http_response_code=code)
            - metric_value(before, counter, http_response_code=code)
            for code in ("200", "400", "500")
        }
        assert counter_deltas == {"200": 1, "400": 1, "500": 0}
        assert metric_value(after, duration + "_count") == 2
        duration_sum = metric_value(after, duration + "_sum")
        assert math.isfinite(duration_sum) and duration_sum >= 0

        bounds = sorted(
            {
                float(s.labels["le"])
                for s in after
                if s.name == duration + "_bucket" and s.labels.get("endpoint") == "/predict"
            }
        )
        assert bounds[-1] == math.inf
        cumulative = [
            sum(
                s.value
                for s in after
                if s.name == duration + "_bucket"
                and s.labels.get("endpoint") == "/predict"
                and float(s.labels["le"]) == bound
            )
            - sum(
                s.value
                for s in before
                if s.name == duration + "_bucket"
                and s.labels.get("endpoint") == "/predict"
                and float(s.labels["le"]) == bound
            )
            for bound in bounds
        ]
        assert cumulative == sorted(cumulative)
        assert cumulative[-1] == 2
        frequencies = [
            current - previous
            for previous, current in zip([0, *cumulative[:-1]], cumulative, strict=True)
        ]
        assert sum(frequencies) == 2 and min(frequencies) >= 0
        required_labels = {
            "endpoint",
            "http_response_code",
            "runner_name",
            "service_name",
            "service_version",
        }
        assert all(required_labels <= s.labels.keys() for s in after if s.name == counter)

        (tmp_path / f"metrics-{attempt}-before.prom").write_text(before_text, encoding="utf-8")
        (tmp_path / f"metrics-{attempt}-after.prom").write_text(after_text, encoding="utf-8")
        measurements.append(
            {
                "cycle": attempt,
                "initial_predict_count": 0,
                "preserved_log_bytes": len(previous_log),
                "appended_events": len(appended),
                "counter_deltas": counter_deltas,
                "count": 2,
                "duration_sum_seconds": duration_sum,
                "mean_latency_ms": duration_sum / 2 * 1000,
                "http_error_percent": 50.0,
                "server_error_percent": 0.0,
                "buckets": [
                    {
                        "le_seconds": "+Inf" if math.isinf(bound) else bound,
                        "cumulative": count,
                        "frequency": frequency,
                    }
                    for bound, count, frequency in zip(bounds, cumulative, frequencies, strict=True)
                ],
            }
        )
        previous_log = current_log
    (tmp_path / "metrics-summary.json").write_text(
        json.dumps(measurements, indent=2, allow_nan=False),
        encoding="utf-8",
    )
