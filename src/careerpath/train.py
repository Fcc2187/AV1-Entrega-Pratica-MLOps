"""Training utilities for the UCI Adult income classifier."""

import hashlib
import json
import pickle
import platform
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd
import sklearn
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    brier_score_loss,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

ALL_COLUMNS = [
    "age",
    "workclass",
    "fnlwgt",
    "education",
    "education-num",
    "marital-status",
    "occupation",
    "relationship",
    "race",
    "sex",
    "capital-gain",
    "capital-loss",
    "hours-per-week",
    "native-country",
    "income",
]

VALID_TARGETS = {"<=50K", ">50K"}
NUMERIC_FEATURES = ["age", "hours-per-week"]
CATEGORICAL_FEATURES = [
    "education",
    "workclass",
    "occupation",
    "marital-status",
]
FEATURES = [
    "age",
    "education",
    "workclass",
    "occupation",
    "marital-status",
    "hours-per-week",
]


def load_adult(path: Path, *, test_file: bool = False) -> pd.DataFrame:
    """Load and normalize one of the original Adult dataset partitions."""
    frame = pd.read_csv(
        path,
        names=ALL_COLUMNS,
        skiprows=1 if test_file else 0,
        skipinitialspace=True,
        na_values=["?"],
    ).dropna(how="all")

    for column in frame.select_dtypes(include="str"):
        frame[column] = frame[column].str.strip()
    frame["income"] = frame["income"].str.removesuffix(".")
    frame["age"] = pd.to_numeric(frame["age"], errors="raise")
    frame["hours-per-week"] = pd.to_numeric(frame["hours-per-week"], errors="raise")

    targets = set(frame["income"].dropna().unique())
    if targets != VALID_TARGETS:
        raise ValueError(f"unexpected target classes: {sorted(targets)}")
    return frame


def remove_test_overlap(
    train: pd.DataFrame, test: pd.DataFrame
) -> tuple[pd.DataFrame, int]:
    """Remove exact full rows from training when they also occur in test."""
    missing = "<MISSING>"
    test_rows = set(test.fillna(missing).itertuples(index=False, name=None))
    overlaps = train.fillna(missing).apply(tuple, axis=1).isin(test_rows)
    return train.loc[~overlaps].reset_index(drop=True), int(overlaps.sum())


def build_pipeline() -> Pipeline:
    """Build the deterministic preprocessing and classification pipeline."""
    preprocessing = ColumnTransformer(
        [
            (
                "numeric",
                Pipeline(
                    [
                        ("imputer", SimpleImputer(strategy="median")),
                        ("scaler", StandardScaler()),
                    ]
                ),
                NUMERIC_FEATURES,
            ),
            (
                "categorical",
                Pipeline(
                    [
                        ("imputer", SimpleImputer(strategy="most_frequent")),
                        ("encoder", OneHotEncoder(handle_unknown="ignore")),
                    ]
                ),
                CATEGORICAL_FEATURES,
            ),
        ]
    )
    return Pipeline(
        [
            ("preprocessing", preprocessing),
            (
                "classifier",
                LogisticRegression(
                    random_state=42,
                    solver="liblinear",
                    max_iter=1000,
                ),
            ),
        ]
    )


def evaluate_classifier(
    estimator: Pipeline | DummyClassifier,
    features: pd.DataFrame,
    target: pd.Series,
) -> dict[str, object]:
    """Calculate the agreed binary-classification metrics."""
    predictions = estimator.predict(features)
    positive_index = list(estimator.classes_).index(">50K")
    probabilities = estimator.predict_proba(features)[:, positive_index]
    positive_target = target.eq(">50K")
    return {
        "accuracy": float(accuracy_score(target, predictions)),
        "balanced_accuracy": float(balanced_accuracy_score(target, predictions)),
        "precision_above_50k": float(
            precision_score(target, predictions, pos_label=">50K", zero_division=0)
        ),
        "recall_above_50k": float(
            recall_score(target, predictions, pos_label=">50K", zero_division=0)
        ),
        "f1_above_50k": float(
            f1_score(target, predictions, pos_label=">50K", zero_division=0)
        ),
        "roc_auc": float(roc_auc_score(positive_target, probabilities)),
        "brier_score": float(brier_score_loss(positive_target, probabilities)),
        "confusion_matrix": confusion_matrix(
            target, predictions, labels=["<=50K", ">50K"]
        ).tolist(),
    }


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def train_and_save(
    train_path: Path,
    test_path: Path,
    model_path: Path,
    metadata_path: Path,
) -> dict[str, object]:
    """Train on Adult's training partition and persist the complete pipeline."""
    original_train = load_adult(train_path)
    test = load_adult(test_path, test_file=True)
    train, overlap_count = remove_test_overlap(original_train, test)
    train_features, train_target = train[FEATURES], train["income"]
    test_features, test_target = test[FEATURES], test["income"]

    pipeline = build_pipeline().fit(train_features, train_target)
    baseline = DummyClassifier(strategy="most_frequent").fit(
        train_features, train_target
    )

    model_path.parent.mkdir(parents=True, exist_ok=True)
    model_path.write_bytes(pickle.dumps(pipeline, protocol=pickle.HIGHEST_PROTOCOL))
    metadata: dict[str, object] = {
        "model_name": "careerpath-adult-income",
        "model_version": "adult-income-v1",
        "dataset": "Census Income (Adult)",
        "dataset_reference": "UCI ID 20; DOI 10.24432/C5GP7S; CC BY 4.0",
        "features": FEATURES,
        "excluded_features": {
            "race": "sensitive attribute excluded from operational predictors",
            "sex": "sensitive attribute excluded from operational predictors",
            "fnlwgt": "survey weight, not a prospect attribute",
            "relationship": "unnecessary household detail",
            "native-country": "unnecessary origin attribute",
            "capital-gain": "financial detail outside the form scope",
            "capital-loss": "financial detail outside the form scope",
            "education-num": "duplicate representation of education",
        },
        "sklearn_version": sklearn.__version__,
        "python_version": platform.python_version(),
        "trained_at": datetime.now(UTC).isoformat(),
        "seed": 42,
        "parameters": {
            "classifier": "LogisticRegression",
            "solver": "liblinear",
            "max_iter": 1000,
            "threshold": 0.5,
        },
        "counts": {
            "train_original": len(original_train),
            "train_used": len(train),
            "test": len(test),
            "overlap_removed": overlap_count,
        },
        "cleaning": [
            "trim whitespace",
            "convert ? to missing",
            "remove terminal dot from test labels",
            "remove exact train rows also present in test",
        ],
        "data_sha256": {
            "adult.data": _sha256(train_path),
            "adult.test": _sha256(test_path),
        },
        "artifact_sha256": _sha256(model_path),
        "metrics": {
            "model": evaluate_classifier(pipeline, test_features, test_target),
            "baseline": evaluate_classifier(baseline, test_features, test_target),
        },
        "class_order": ["<=50K", ">50K"],
        "limitations": [
            "historical 1994 US Census income proxy, not a career outcome",
            "excluded sensitive attributes do not eliminate proxy bias",
            "unknown categories execute but have no learned category effect",
            "not validated for automated decisions about people",
        ],
    }
    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    metadata_path.write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return metadata


def main() -> None:
    """Train the versioned project artifact from the explicit local dataset."""
    root = Path(__file__).resolve().parents[2]
    metadata = train_and_save(
        root / "data" / "raw" / "adult.data",
        root / "data" / "raw" / "adult.test",
        root / "models" / "adult-income-v1.pkl",
        root / "models" / "metadata.json",
    )
    print(json.dumps({"counts": metadata["counts"], "metrics": metadata["metrics"]}, indent=2))


if __name__ == "__main__":
    main()
