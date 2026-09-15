"""Verified model loading and inference utilities."""

import hashlib
import json
import pickle
from collections.abc import Mapping
from pathlib import Path

import pandas as pd
import sklearn
from sklearn.pipeline import Pipeline


def load_artifact(model_path: Path, metadata_path: Path) -> tuple[Pipeline, dict]:
    """Verify compatibility and integrity before loading the trusted artifact."""
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    if metadata["sklearn_version"] != sklearn.__version__:
        raise RuntimeError(
            "scikit-learn version mismatch: "
            f"artifact={metadata['sklearn_version']} runtime={sklearn.__version__}"
        )
    artifact = model_path.read_bytes()
    actual_hash = hashlib.sha256(artifact).hexdigest()
    if actual_hash != metadata["artifact_sha256"]:
        raise ValueError("model artifact hash does not match metadata")
    pipeline = pickle.loads(artifact)  # noqa: S301 - verified trusted local artifact
    if not isinstance(pipeline, Pipeline):
        raise TypeError("model artifact is not a scikit-learn Pipeline")
    return pipeline, metadata


def predict_income(
    pipeline: Pipeline,
    metadata: dict,
    profile: Mapping[str, object],
) -> dict[str, object]:
    """Return the stable prediction contract for one validated profile."""
    features = pd.DataFrame(
        [
            {
                "age": profile["age"],
                "education": profile["education"],
                "workclass": profile["workclass"],
                "occupation": profile["occupation"],
                "marital-status": profile["marital_status"],
                "hours-per-week": profile["hours_per_week"],
            }
        ]
    )
    positive_index = list(pipeline.classes_).index(">50K")
    probability = float(pipeline.predict_proba(features)[0, positive_index])
    return {
        "income_class_proxy": ">50K" if probability >= 0.5 else "<=50K",
        "probability_above_50k": probability,
        "model_version": metadata["model_version"],
    }
