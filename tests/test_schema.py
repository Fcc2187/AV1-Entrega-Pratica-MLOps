import pytest
from pydantic import ValidationError

from careerpath.schema import Prediction, Profile


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


def test_profile_trims_strings_and_accepts_required_nulls() -> None:
    profile = Profile.model_validate(
        valid_profile(
            education="  Bachelors  ",
            workclass=None,
            occupation=None,
        )
    )

    assert profile.education == "Bachelors"
    assert profile.workclass is None
    assert profile.occupation is None


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("age", 16),
        ("age", 101),
        ("age", True),
        ("age", "35"),
        ("hours_per_week", 0),
        ("hours_per_week", 100),
        ("hours_per_week", False),
        ("education", ""),
        ("education", "?"),
        ("workclass", "?"),
        ("occupation", "?"),
    ],
)
def test_profile_rejects_invalid_field_values(field: str, value: object) -> None:
    with pytest.raises(ValidationError):
        Profile.model_validate(valid_profile(**{field: value}))


def test_profile_rejects_missing_and_extra_fields() -> None:
    missing = valid_profile()
    missing.pop("occupation")

    with pytest.raises(ValidationError):
        Profile.model_validate(missing)
    with pytest.raises(ValidationError):
        Profile.model_validate(valid_profile(unknown="value"))


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("income_class_proxy", "unknown"),
        ("probability_above_50k", float("inf")),
        ("probability_above_50k", -0.1),
        ("probability_above_50k", 1.1),
    ],
)
def test_prediction_rejects_invalid_output(field: str, value: object) -> None:
    payload: dict[str, object] = {
        "income_class_proxy": "<=50K",
        "probability_above_50k": 0.25,
        "model_version": "adult-income-v1",
    }
    payload[field] = value

    with pytest.raises(ValidationError):
        Prediction.model_validate(payload)
