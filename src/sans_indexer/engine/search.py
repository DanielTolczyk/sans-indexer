from __future__ import annotations

import sqlite3
from typing import Iterable

from sans_indexer.models import IndexEntry, SearchResult


class SearchEngine:
    """In-memory SQLite FTS5 full-text search engine."""

    def __init__(self) -> None:
        self._conn = sqlite3.connect(":memory:")
        self._create_schema()

    def _create_schema(self) -> None:
        """Initializes the FTS5 virtual table."""
        cursor = self._conn.cursor()
        cursor.execute(
            """
            CREATE VIRTUAL TABLE index_fts USING fts5(
                term,
                book UNINDEXED,
                page UNINDEXED,
                category,
                notes,
                synonyms,
                tokenize='porter unicode61'
            );
            """
        )
        self._conn.commit()

    def index_entries(self, entries: Iterable[IndexEntry]) -> None:
        """Loads entries into the in-memory FTS5 table."""
        cursor = self._conn.cursor()
        data = [
            (
                e.term,
                e.book,
                str(e.page),
                e.category,
                e.notes,
                ", ".join(e.synonyms),
            )
            for e in entries
        ]
        cursor.executemany(
            """
            INSERT INTO index_fts (term, book, page, category, notes, synonyms)
            VALUES (?, ?, ?, ?, ?, ?);
            """,
            data,
        )
        self._conn.commit()

    def search(self, query: str, limit: int = 25) -> list[SearchResult]:
        """Executes a ranked FTS5 search with prefix matching support."""
        clean_query = query.strip()
        if not clean_query:
            return []

        # Sanitize double quotes and prepare prefix query for tokens
        tokens = [t.replace('"', '""') for t in clean_query.split() if t.strip()]
        if not tokens:
            return []

        # Appends wildcard to the final token for prefix search (e.g., 'kerb*')
        fts_query = " ".join(tokens[:-1] + [f"{tokens[-1]}*"])

        cursor = self._conn.cursor()
        # bm25 weights: term(5.0), category(1.0), notes(2.0), synonyms(4.0)
        cursor.execute(
            """
            SELECT term, book, page, category, notes, synonyms,
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
            term, book, page_str, category, notes, synonyms_str, score = row
            synonyms_list = [s.strip() for s in synonyms_str.split(",") if s.strip()]

            entry = IndexEntry(
                term=term,
                book=book,
                page=int(page_str),
                category=category,
                notes=notes,
                synonyms=synonyms_list,
            )

            results.append(SearchResult(entry=entry, score=score))

        return results

    def close(self) -> None:
        """Closes the in-memory SQLite connection."""
        self._conn.close()