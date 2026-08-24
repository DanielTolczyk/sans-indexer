from __future__ import annotations

import csv
import os
from pathlib import Path
from typing import Iterator

from sans_indexer.models import IndexEntry
from sans_indexer.storage.base import BaseStorage

CSV_FIELDNAMES = ["term", "book", "page", "category", "notes", "synonyms"]


class CSVStorage(BaseStorage):
    """Local CSV file storage implementation."""

    def __init__(self, file_path: str | Path) -> None:
        self.file_path = Path(file_path)

    def load_all(self) -> Iterator[IndexEntry]:
        """Yields all IndexEntry records from the CSV file."""
        if not self.file_path.exists():
            return

        with open(self.file_path, mode="r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if not row or not row.get("term"):
                    continue
                yield IndexEntry(
                    term=row["term"],
                    book=row["book"],
                    page=int(row["page"]),
                    category=row.get("category", "General"),
                    notes=row.get("notes", ""),
                    synonyms=row.get("synonyms", ""),
                )

    def add(self, entry: IndexEntry) -> None:
        """Appends a single IndexEntry to the CSV file."""
        # Ensure parent directory exists (e.g. data/)
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        file_exists = self.file_path.exists() and self.file_path.stat().st_size > 0

        with open(self.file_path, mode="a", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_FIELDNAMES)
            if not file_exists:
                writer.writeheader()
            writer.writerow(entry.to_csv_row())