from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from careerpath.model import load_artifact, predict_income
from careerpath.train import (
    build_pipeline,
    load_adult,
    remove_test_overlap,
    train_and_save,
)

ROW_A = (
    "39, State-gov, 77516, Bachelors, 13, Never-married, Adm-clerical, "
    "Not-in-family, White, Male, 2174, 0, 40, United-States, <=50K"
)
ROW_B = (
    "50, Self-emp-not-inc, 83311, Bachelors, 13, Married-civ-spouse, ?, "
    "Husband, White, Male, 0, 0, 13, United-States, >50K"
)
ROW_C = (
    "28, Private, 338409, HS-grad, 9, Married-civ-spouse, Craft-repair, "
    "Husband, White, Male, 0, 0, 40, Cuba, <=50K"
)
ROW_D = (
    "31, Private, 45781, Masters, 14, Never-married, Prof-specialty, "
    "Not-in-family, White, Female, 14084, 0, 50, United-States, >50K"
)


def write_rows(path: Path, *rows: str) -> None:
    path.write_text("\n".join(rows) + "\n", encoding="utf-8")


def test_load_adult_normalizes_test_labels_and_missing_values(tmp_path: Path) -> None:
    test_path = tmp_path / "adult.test"
    write_rows(test_path, "|1x3 Cross validator", f"{ROW_A}.", f"{ROW_B}.")

    frame = load_adult(test_path, test_file=True)

    assert frame["income"].tolist() == ["<=50K", ">50K"]
    assert frame.loc[0, "workclass"] == "State-gov"
    assert pd.isna(frame.loc[1, "occupation"])
    assert frame["age"].tolist() == [39, 50]
    assert frame["hours-per-week"].tolist() == [40, 13]


def test_remove_test_overlap_uses_the_complete_row(tmp_path: Path) -> None:
    train_path = tmp_path / "adult.data"
    test_path = tmp_path / "adult.test"
    write_rows(train_path, ROW_A, ROW_B, ROW_C)
    write_rows(test_path, "|1x3 Cross validator", f"{ROW_A}.", f"{ROW_D}.")
    train = load_adult(train_path)
    test = load_adult(test_path, test_file=True)

    filtered, removed = remove_test_overlap(train, test)

    assert removed == 1
    assert filtered["age"].tolist() == [50, 28]
    assert filtered["income"].tolist() == [">50K", "<=50K"]


def test_pipeline_predicts_probability_for_unseen_category() -> None:
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
    profile = features.iloc[[0]].copy()
    profile["workclass"] = "Without-pay"

    probabilities = pipeline.predict_proba(profile)

    assert probabilities.shape == (1, 2)
    assert np.isfinite(probabilities).all()


def test_train_persists_metrics_and_rejects_tampered_artifact(tmp_path: Path) -> None:
    train_path = tmp_path / "adult.data"
    test_path = tmp_path / "adult.test"
    model_path = tmp_path / "adult-income-v1.pkl"
    metadata_path = tmp_path / "metadata.json"
    write_rows(train_path, ROW_A, ROW_B, ROW_C, ROW_D)
    write_rows(
        test_path,
        "|1x3 Cross validator",
        f"{ROW_A.replace('39,', '40,', 1)}.",
        f"{ROW_B.replace('50,', '51,', 1)}.",
        f"{ROW_C.replace('28,', '29,', 1)}.",
        f"{ROW_D.replace('31,', '32,', 1)}.",
    )

    metadata = train_and_save(train_path, test_path, model_path, metadata_path)

    assert model_path.is_file()
    assert metadata_path.is_file()
    assert metadata["counts"] == {
        "train_original": 4,
        "train_used": 4,
        "test": 4,
        "overlap_removed": 0,
    }
    assert set(metadata["metrics"]) == {"model", "baseline"}
    assert len(metadata["metrics"]["model"]["confusion_matrix"]) == 2
    assert metadata["artifact_sha256"]
    assert set(metadata["data_sha256"]) == {"adult.data", "adult.test"}

    pipeline, loaded_metadata = load_artifact(model_path, metadata_path)
    result = predict_income(
        pipeline,
        loaded_metadata,
        {
            "age": 42,
            "education": "Bachelors",
            "workclass": "Private",
            "occupation": "Sales",
            "marital_status": "Never-married",
            "hours_per_week": 40,
        },
    )
    assert result["model_version"] == "adult-income-v1"

    model_path.write_bytes(model_path.read_bytes() + b"tampered")
    with pytest.raises(ValueError, match="hash"):
        load_artifact(model_path, metadata_path)
