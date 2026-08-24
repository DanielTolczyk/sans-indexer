from __future__ import annotations

import sqlite3
from typing import Iterable

from sans_indexer.models import IndexEntry, SearchResult


class SearchEngine:
    """In-memory SQLite FTS5 full-text search engine with BM25 ranking."""

    def __init__(self, entries: Iterable[IndexEntry] | None = None) -> None:
        self._conn = sqlite3.connect(":memory:")
        self._init_schema()
        if entries:
            self.index_entries(entries)

    def _init_schema(self) -> None:
        cursor = self._conn.cursor()
        cursor.execute(
            """
            CREATE VIRTUAL TABLE index_fts USING fts5(
                term,
                book,
                page UNINDEXED,
                category,
                notes,
                synonyms,
                is_lab UNINDEXED,
                tokenize='porter unicode61'
            );
            """
        )
        self._conn.commit()

    def index_entries(self, entries: Iterable[IndexEntry]) -> None:
        """Populates the in-memory FTS5 virtual table."""
        cursor = self._conn.cursor()
        cursor.execute("DELETE FROM index_fts;")
        data = [
            (
                e.term,
                e.book,
                e.page,
                e.category,
                e.notes,
                ", ".join(e.synonyms),
                "1" if e.is_lab else "0",
            )
            for e in entries
        ]
        cursor.executemany(
            """
            INSERT INTO index_fts (term, book, page, category, notes, synonyms, is_lab)
            VALUES (?, ?, ?, ?, ?, ?, ?);
            """,
            data,
        )
        self._conn.commit()

    def search(self, query: str, limit: int = 25) -> list[SearchResult]:
        """Executes a ranked FTS5 search with prefix matching support."""
        clean_query = query.strip()
        if not clean_query:
            return []

        tokens = [t.replace('"', '""') for t in clean_query.split() if t.strip()]
        if not tokens:
            return []

        fts_query = " ".join(tokens[:-1] + [f"{tokens[-1]}*"])

        cursor = self._conn.cursor()
        cursor.execute(
            """
            SELECT term, book, page, category, notes, synonyms, is_lab,
                   bm25(index_fts, 5.0, 1.0, 2.0, 4.0) AS score
            FROM index_fts
            WHERE index_fts MATCH ?
            ORDER BY score ASC
            LIMIT ?;
            """,
            (fts_query, limit),
        )

        results: list[SearchResult] = []
        for row in cursor.fetchall():
            term, book, page_str, category, notes, synonyms_str, is_lab_str, score = row
            synonyms_list = [s.strip() for s in synonyms_str.split(",") if s.strip()]
            is_lab = is_lab_str == "1"

            entry = IndexEntry(
                term=term,
                book=book,
                page=page_str,
                category=category,
                notes=notes,
                synonyms=synonyms_list,
                is_lab=is_lab,
            )

            results.append(SearchResult(entry=entry, score=score))

        return results

    def close(self) -> None:
        """Closes the underlying SQLite in-memory connection."""
        if self._conn:
            self._conn.close()

    def __enter__(self) -> SearchEngine:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()