import json
import math
import subprocess
import sys
from pathlib import Path
from textwrap import dedent

import pytest
from starlette.testclient import TestClient

from careerpath.service import CareerPathService

PROJECT_ROOT = Path(__file__).parents[1]


def valid_profile(**changes: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "age": 35,
        "education": "Bachelors",
        "workclass": "Private",
        "occupation": "Tech-support",
        "marital_status": "Never-married",
        "hours_per_week": 40,
    }
    payload.update(changes)
    return payload


@pytest.fixture(scope="module")
def client():
    with TestClient(CareerPathService.to_asgi()) as test_client:
        yield test_client


def test_health_reports_loaded_model(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "model_version": "adult-income-v1",
    }


def test_predict_accepts_root_profile_and_returns_contract(client: TestClient) -> None:
    response = client.post("/predict", json=valid_profile())

    assert response.status_code == 200
    body = response.json()
    assert set(body) == {
        "income_class_proxy",
        "probability_above_50k",
        "model_version",
    }
    assert body["income_class_proxy"] in {"<=50K", ">50K"}
    assert math.isfinite(body["probability_above_50k"])
    assert 0 <= body["probability_above_50k"] <= 1
    assert body["model_version"] == "adult-income-v1"


def test_predict_accepts_unknown_and_nullable_categories(client: TestClient) -> None:
    response = client.post(
        "/predict",
        json=valid_profile(
            workclass="Gig-platform",
            occupation=None,
        ),
    )

    assert response.status_code == 200


@pytest.mark.parametrize(
    "payload",
    [
        valid_profile(age=-1),
        valid_profile(age="35"),
        valid_profile(extra="value"),
    ],
)
def test_predict_rejects_invalid_profiles(
    client: TestClient, payload: dict[str, object]
) -> None:
    response = client.post("/predict", json=payload)

    assert response.status_code == 400


def test_predict_rejects_malformed_json(client: TestClient) -> None:
    response = client.post(
        "/predict",
        content="{",
        headers={"content-type": "application/json"},
    )

    assert response.status_code == 400


@pytest.mark.parametrize("filename", ["case-1.json", "case-2.json", "case-3.json"])
def test_valid_examples_are_executable(client: TestClient, filename: str) -> None:
    payload = json.loads((PROJECT_ROOT / "examples" / filename).read_text("utf-8"))

    response = client.post("/predict", json=payload)

    assert response.status_code == 200


def test_invalid_example_is_rejected(client: TestClient) -> None:
    payload = json.loads((PROJECT_ROOT / "examples" / "invalid.json").read_text("utf-8"))

    response = client.post("/predict", json=payload)

    assert response.status_code == 400


def test_service_startup_fails_without_local_artifact(tmp_path: Path) -> None:
    copied_service = tmp_path / "src" / "careerpath" / "service.py"
    copied_service.parent.mkdir(parents=True)
    copied_service.write_text(
        (PROJECT_ROOT / "src" / "careerpath" / "service.py").read_text("utf-8"),
        encoding="utf-8",
    )
    script = dedent(
        f"""
        import importlib.util
        from unittest.mock import patch
        import careerpath.train as training

        with (
            patch(
                "urllib.request.urlopen",
                side_effect=AssertionError("network fallback attempted"),
            ),
            patch.object(
                training,
                "train_and_save",
                side_effect=AssertionError("training fallback attempted"),
            ),
            patch.object(
                training,
                "main",
                side_effect=AssertionError("training fallback attempted"),
            ),
        ):
            spec = importlib.util.spec_from_file_location(
                "missing_artifact_service", {str(copied_service)!r}
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
        """
    )

    result = subprocess.run(
        [sys.executable, "-c", script],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
        timeout=10,
    )

    assert result.returncode != 0
    assert "FileNotFoundError" in result.stderr
    assert "metadata.json" in result.stderr
    assert not (tmp_path / "data").exists()
