import pandas as pd
import pytest
from numpy import array

from careerpath.model import load_artifact, predict_income
from careerpath.train import build_pipeline


class FixedProbabilityPipeline:
    classes_ = ["<=50K", ">50K"]

    def __init__(self, probability: float) -> None:
        self.probability = probability

    def predict_proba(self, _features: pd.DataFrame):
        return array([[1 - self.probability, self.probability]])


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


def test_predict_income_sends_null_categories_to_trained_imputers() -> None:
    features = pd.DataFrame(
        {
            "age": [22, 28, 35, 44, 52, 61],
            "education": ["HS-grad", "Bachelors", "Masters"] * 2,
            "workclass": ["Private"] * 4 + ["State-gov", "Self-emp"],
            "occupation": ["Sales"] * 4 + ["Adm-clerical", "Prof-specialty"],
            "marital-status": ["Never-married"] * 3 + ["Married-civ-spouse"] * 3,
            "hours-per-week": [20, 35, 40, 45, 50, 60],
        }
    )
    target = pd.Series(["<=50K"] * 3 + [">50K"] * 3)
    pipeline = build_pipeline().fit(features, target)
    profile = {
        "age": 42,
        "education": "Bachelors",
        "workclass": None,
        "occupation": None,
        "marital_status": "Never-married",
        "hours_per_week": 40,
    }

    null_result = predict_income(pipeline, {"model_version": "test-v1"}, profile)
    profile.update(workclass="Private", occupation="Sales")
    mode_result = predict_income(pipeline, {"model_version": "test-v1"}, profile)

    assert null_result["probability_above_50k"] == pytest.approx(
        mode_result["probability_above_50k"]
    )


@pytest.mark.parametrize(
    ("probability", "expected_class"),
    [(0.499, "<=50K"), (0.5, ">50K")],
)
def test_predict_income_uses_documented_threshold(
    probability: float, expected_class: str
) -> None:
    profile = {
        "age": 42,
        "education": "Bachelors",
        "workclass": "Private",
        "occupation": "Sales",
        "marital_status": "Never-married",
        "hours_per_week": 40,
    }

    result = predict_income(
        FixedProbabilityPipeline(probability),  # type: ignore[arg-type]
        {"model_version": "test-v1"},
        profile,
    )

    assert result["income_class_proxy"] == expected_class
    assert result["probability_above_50k"] == probability
