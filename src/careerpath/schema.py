"""HTTP input and output contracts."""

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StrictInt, StrictStr, field_validator

ShortText = Annotated[StrictStr, Field(min_length=1, max_length=80)]
Workclass = Literal[
    "Private",
    "Self-emp-not-inc",
    "Self-emp-inc",
    "Federal-gov",
    "Local-gov",
    "State-gov",
    "Without-pay",
    "Never-worked",
]
Education = Literal[
    "Bachelors",
    "Some-college",
    "11th",
    "HS-grad",
    "Prof-school",
    "Assoc-acdm",
    "Assoc-voc",
    "9th",
    "7th-8th",
    "12th",
    "Masters",
    "1st-4th",
    "10th",
    "Doctorate",
    "5th-6th",
    "Preschool",
]
MaritalStatus = Literal[
    "Married-civ-spouse",
    "Divorced",
    "Never-married",
    "Separated",
    "Widowed",
    "Married-spouse-absent",
    "Married-AF-spouse",
]
Occupation = Literal[
    "Tech-support",
    "Craft-repair",
    "Other-service",
    "Sales",
    "Exec-managerial",
    "Prof-specialty",
    "Handlers-cleaners",
    "Machine-op-inspct",
    "Adm-clerical",
    "Farming-fishing",
    "Transport-moving",
    "Priv-house-serv",
    "Protective-serv",
    "Armed-Forces",
]


class Profile(BaseModel):
    """One profile accepted by the prediction endpoint."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    age: Annotated[StrictInt, Field(ge=17, le=100)]
    education: Education
    workclass: Workclass | None
    occupation: Occupation | None
    marital_status: MaritalStatus
    hours_per_week: Annotated[StrictInt, Field(ge=1, le=99)]

    @field_validator("education", "workclass", "occupation", "marital_status", mode="before")
    @classmethod
    def strip_category_whitespace(cls, value: object) -> object:
        return value.strip() if isinstance(value, str) else value

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
