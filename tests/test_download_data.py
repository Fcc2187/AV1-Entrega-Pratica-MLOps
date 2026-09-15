from io import BytesIO
from pathlib import Path
from runpy import run_path
from zipfile import ZipFile

import pytest

extract_dataset = run_path(
    Path(__file__).parents[1] / "scripts" / "download_data.py"
)["extract_dataset"]


def make_zip(*names: str) -> bytes:
    archive = BytesIO()
    with ZipFile(archive, "w") as zipped:
        for name in names:
            zipped.writestr(name, f"contents of {name}")
    return archive.getvalue()


def test_extract_dataset_writes_only_required_files(tmp_path) -> None:
    archive = make_zip("adult.data", "adult.test", "adult.names", "Index")

    paths = extract_dataset(archive, tmp_path)

    assert {path.name for path in paths} == {
        "adult.data",
        "adult.test",
        "adult.names",
    }
    assert {path.name for path in tmp_path.iterdir()} == {
        "adult.data",
        "adult.test",
        "adult.names",
    }


def test_extract_dataset_rejects_missing_member(tmp_path) -> None:
    archive = make_zip("adult.data", "adult.test")

    with pytest.raises(ValueError, match="adult.names"):
        extract_dataset(archive, tmp_path)
