"""HTTP input and output contracts."""

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StrictInt, StrictStr, field_validator

ShortText = Annotated[StrictStr, Field(min_length=1, max_length=80)]


class Profile(BaseModel):
    """One profile accepted by the prediction endpoint."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    age: Annotated[StrictInt, Field(ge=17, le=100)]
    education: ShortText
    workclass: ShortText | None
    occupation: ShortText | None
    marital_status: ShortText
    hours_per_week: Annotated[StrictInt, Field(ge=1, le=99)]

    @field_validator("education", "workclass", "occupation", "marital_status")
    @classmethod
    def reject_missing_marker(cls, value: str | None) -> str | None:
        if value == "?":
            raise ValueError("question mark is not a valid category")
        return value


class Prediction(BaseModel):
    """Stable response returned by the prediction endpoint."""

    model_config = ConfigDict(extra="forbid")

    income_class_proxy: Literal["<=50K", ">50K"]
    probability_above_50k: Annotated[
        float, Field(ge=0, le=1, allow_inf_nan=False)
    ]
    model_version: ShortText
