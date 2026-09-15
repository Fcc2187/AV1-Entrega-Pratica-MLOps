"""Explicitly download the original Adult dataset files from UCI."""

from io import BytesIO
from pathlib import Path
from urllib.request import urlopen
from zipfile import ZipFile

DATASET_URL = "https://archive.ics.uci.edu/static/public/20/census+income.zip"
REQUIRED_FILES = ("adult.data", "adult.test", "adult.names")


def extract_dataset(archive: bytes, destination: Path) -> list[Path]:
    """Validate an Adult ZIP and write only the required files."""
    with ZipFile(BytesIO(archive)) as zipped:
        missing = set(REQUIRED_FILES) - set(zipped.namelist())
        if missing:
            raise ValueError(f"dataset archive is missing: {', '.join(sorted(missing))}")
        destination.mkdir(parents=True, exist_ok=True)
        paths = [destination / name for name in REQUIRED_FILES]
        for path, name in zip(paths, REQUIRED_FILES, strict=True):
            path.write_bytes(zipped.read(name))
    return paths


def download_dataset(destination: Path = Path("data/raw")) -> list[Path]:
    """Download the fixed official UCI archive and extract required members."""
    with urlopen(DATASET_URL, timeout=60) as response:  # noqa: S310 - fixed HTTPS URL
        return extract_dataset(response.read(), destination)


if __name__ == "__main__":
    for downloaded_path in download_dataset():
        print(downloaded_path)
