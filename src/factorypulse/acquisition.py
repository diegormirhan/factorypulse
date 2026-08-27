from __future__ import annotations

import shutil
import tempfile
import urllib.request
import zipfile
from pathlib import Path


def download_dataset(source_url: str, destination: Path) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="factorypulse-") as temporary_directory:
        archive_path = Path(temporary_directory) / "dataset.zip"
        urllib.request.urlretrieve(source_url, archive_path)
        with zipfile.ZipFile(archive_path) as archive:
            csv_members = [name for name in archive.namelist() if name.lower().endswith(".csv")]
            if len(csv_members) != 1:
                raise ValueError("Expected exactly one CSV file in the dataset archive.")
            with archive.open(csv_members[0]) as source, destination.open("wb") as target:
                shutil.copyfileobj(source, target)
    return destination
