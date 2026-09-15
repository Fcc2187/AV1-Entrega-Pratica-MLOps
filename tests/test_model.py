import pandas as pd
import pytest

from careerpath.model import load_artifact, predict_income
from careerpath.train import build_pipeline


def test_predict_income_maps_api_fields_and_returns_contract() -> None:
    features = pd.DataFrame(
        {
            "age": [22, 28, 35, 44, 52, 61],
            "education": ["HS-grad", "Bachelors", "Masters"] * 2,
            "workclass": ["Private", "State-gov", "Self-emp"] * 2,
            "occupation": ["Sales", "Adm-clerical", "Prof-specialty"] * 2,
            "marital-status": ["Never-married"] * 3 + ["Married-civ-spouse"] * 3,
            "hours-per-week": [20, 35, 40, 45, 50, 60],
        }
    )
    target = pd.Series(["<=50K"] * 3 + [">50K"] * 3)
    pipeline = build_pipeline().fit(features, target)

    result = predict_income(
        pipeline,
        {"model_version": "test-v1"},
        {
            "age": 42,
            "education": "Doctorate",
            "workclass": "Never-worked",
            "occupation": "Prof-specialty",
            "marital_status": "Married-civ-spouse",
            "hours_per_week": 50,
        },
    )

    assert set(result) == {
        "income_class_proxy",
        "probability_above_50k",
        "model_version",
    }
    assert result["income_class_proxy"] in {"<=50K", ">50K"}
    assert 0 <= result["probability_above_50k"] <= 1
    assert result["model_version"] == "test-v1"


def test_load_artifact_rejects_missing_files(tmp_path) -> None:
    missing_model = tmp_path / "missing.pkl"
    missing_metadata = tmp_path / "missing.json"

    with pytest.raises(FileNotFoundError) as error:
        load_artifact(missing_model, missing_metadata)

    assert error.value.filename == str(missing_metadata)
