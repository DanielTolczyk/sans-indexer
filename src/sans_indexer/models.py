from __future__ import annotations

import re
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class IndexEntry(BaseModel):
    """Represents a single verified index entry for an open-book exam."""

    term: str = Field(..., min_length=1, description="Primary concept, protocol, or command")
    book: str = Field(..., min_length=1, description="Course book identifier (e.g., 'B1', 'Book 1')")
    page: int = Field(..., ge=1, description="Page number within the specified book")
    category: str = Field(default="General", description="Subject taxonomy or domain")
    notes: str = Field(default="", description="Quick syntax, context, or key takeaways")
    synonyms: list[str] = Field(default_factory=list, description="Search aliases and alternate names")

    @field_validator("term", "book", "category", "notes", mode="before")
    @classmethod
    def strip_whitespace(cls, v: str) -> str:
        if isinstance(v, str):
            return v.strip()
        return v

    @field_validator("synonyms", mode="before")
    @classmethod
    def parse_synonyms(cls, v: str | list[str]) -> list[str]:
        if isinstance(v, str):
            if not v.strip():
                return []
            return [s.strip() for s in re.split(r"[,;]", v) if s.strip()]
        return v

    @property
    def sort_key(self) -> str:
        """Normalized key for alphabetical collation."""
        clean = re.sub(r"^[^a-zA-Z0-9]+", "", self.term.lower())
        return clean or self.term.lower()

    @property
    def letter_group(self) -> str:
        """Returns the primary section header character ('A'-'Z' or '#')."""
        key = self.sort_key
        if key and key[0].isalpha():
            return key[0].upper()
        return "#"

    def to_csv_row(self) -> dict[str, str]:
        return {
            "term": self.term,
            "book": self.book,
            "page": str(self.page),
            "category": self.category,
            "notes": self.notes,
            "synonyms": ", ".join(self.synonyms),
        }


class SearchResult(BaseModel):
    """Ranked search result container."""

    entry: IndexEntry
    score: float = 0.0
    matched_field: Optional[str] = None