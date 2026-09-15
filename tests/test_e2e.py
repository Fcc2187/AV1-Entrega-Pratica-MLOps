import json
import os
import shutil
import signal
import socket
import subprocess
import time
from pathlib import Path
from typing import IO
from urllib.error import URLError
from urllib.request import Request, urlopen

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
    with urlopen(request, timeout=2) as response:
        return response.status, json.load(response)


def start_service(port: int, log: IO[str]) -> subprocess.Popen[str]:
    uv = shutil.which("uv")
    assert uv is not None, "uv is required to run the documented service command"
    options: dict[str, object] = {
        "cwd": PROJECT_ROOT,
        "env": {**os.environ, "BENTOML_DO_NOT_TRACK": "True"},
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

    for attempt in range(2):
        log_path = tmp_path / f"service-{attempt}.log"
        with log_path.open("w", encoding="utf-8") as log:
            process = start_service(port, log)
            try:
                health = wait_for_health(process, port, log, log_path)
                status, prediction = request_json(port, "/predict", profile)
            finally:
                stop_service(process, port)

        assert process.poll() is not None
        assert health == {"status": "ok", "model_version": "adult-income-v1"}
        assert status == 200
        assert prediction["income_class_proxy"] in {"<=50K", ">50K"}
        assert 0 <= prediction["probability_above_50k"] <= 1
        assert prediction["model_version"] == "adult-income-v1"
