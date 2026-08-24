from __future__ import annotations

import re
from pydantic import BaseModel, Field, field_validator


class IndexEntry(BaseModel):
    """Represents a single indexed term/concept for SANS/GIAC exam preparation."""

    term: str = Field(..., description="The main concept, tool, or syntax term.")
    book: str = Field(..., description="Book identifier (e.g., 'B1', 'B2', 'Workbook').")
    page: str = Field(..., description="Page number or range (e.g., '45', '45-48', '12, 15').")
    category: str = Field(default="General", description="Subject category (e.g., 'Auth', 'Forensics').")
    notes: str = Field(default="", description="Key syntax, short description, or context.")
    synonyms: list[str] = Field(default_factory=list, description="Alternative names or abbreviations.")
    is_lab: bool = Field(default=False, description="Whether this concept is from a hands-on lab exercise.")

    @field_validator("term", "book", "category", mode="before")
    @classmethod
    def strip_strings(cls, v: str) -> str:
        if isinstance(v, str):
            return v.strip()
        return v

    @field_validator("page", mode="before")
    @classmethod
    def normalize_page(cls, v: int | str) -> str:
        s = str(v).strip()
        if not s:
            raise ValueError("Page cannot be empty.")
        return s

    @property
    def start_page_num(self) -> int:
        """Extracts the leading integer for sorting purposes (e.g., '45-48' -> 45)."""
        match = re.search(r"\d+", self.page)
        return int(match.group()) if match else 0

    @property
    def sort_key(self) -> tuple[str, str, int]:
        """Natural sort key: normalized term, book name, then starting page number."""
        return (self.term.lower(), self.book.lower(), self.start_page_num)

    @property
    def letter_group(self) -> str:
        """Determines the alphabetical header group ('A'-'Z' or '#')."""
        if not self.term:
            return "#"
        first_char = self.term[0].upper()
        return first_char if first_char.isalpha() else "#"


class SearchResult(BaseModel):
    """Wrapper for search results containing the entry and relevance score."""

    entry: IndexEntry
    score: float = Field(..., description="BM25 search relevance score.")

    @property
    def rank(self) -> float:
        return self.score