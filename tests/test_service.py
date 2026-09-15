import json
import math
from pathlib import Path

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
