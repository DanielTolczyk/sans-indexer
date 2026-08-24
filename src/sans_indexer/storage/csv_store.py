from __future__ import annotations

import csv
from pathlib import Path
from typing import Generator

from sans_indexer.models import IndexEntry

FIELDNAMES = ["term", "book", "page", "category", "notes", "synonyms", "is_lab"]


class CSVStorage:
    """Handles flat-file CSV persistence and merging for indexed entries."""

    def __init__(self, file_path: str | Path) -> None:
        self.file_path = Path(file_path)
        self._ensure_file_exists()

    def _ensure_file_exists(self) -> None:
        if not self.file_path.exists():
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.file_path, mode="w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
                writer.writeheader()

    def add(self, entry: IndexEntry) -> None:
        """Appends a new entry to the CSV file."""
        with open(self.file_path, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writerow(
                {
                    "term": entry.term,
                    "book": entry.book,
                    "page": entry.page,
                    "category": entry.category,
                    "notes": entry.notes,
                    "synonyms": ",".join(entry.synonyms),
                    "is_lab": "true" if entry.is_lab else "false",
                }
            )

    def load_all(self) -> Generator[IndexEntry, None, None]:
        """Loads and yields all entries from the CSV file."""
        if not self.file_path.exists():
            return

        with open(self.file_path, mode="r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                synonyms_raw = row.get("synonyms", "")
                synonyms = [s.strip() for s in synonyms_raw.split(",") if s.strip()]
                is_lab_raw = row.get("is_lab", "false")
                is_lab = str(is_lab_raw).strip().lower() in ("true", "1", "yes")

                yield IndexEntry(
                    term=row["term"],
                    book=row["book"],
                    page=row["page"],
                    category=row.get("category", "General"),
                    notes=row.get("notes", ""),
                    synonyms=synonyms,
                    is_lab=is_lab,
                )

    def merge_from(self, source_path: str | Path) -> tuple[int, int]:
        """Merges entries from another CSV into this storage, deduplicating on (term, book, page)."""
        source_storage = CSVStorage(source_path)
        existing_entries = list(self.load_all())
        
        existing_keys = {
            (e.term.strip().lower(), e.book.strip().lower(), str(e.page).strip().lower())
            for e in existing_entries
        }

        added = 0
        skipped = 0
        for entry in source_storage.load_all():
            key = (entry.term.strip().lower(), entry.book.strip().lower(), str(entry.page).strip().lower())
            if key not in existing_keys:
                self.add(entry)
                existing_keys.add(key)
                added += 1
            else:
                skipped += 1

        return added, skipped