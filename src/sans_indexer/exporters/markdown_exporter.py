from __future__ import annotations

from itertools import groupby
from typing import Iterable

from sans_indexer.models import IndexEntry


def export_to_markdown(entries: Iterable[IndexEntry]) -> str:
    """Renders sorted entries into a letter-grouped Markdown table document."""
    sorted_entries = sorted(entries, key=lambda e: (e.letter_group, e.sort_key))
    sections: list[str] = ["# Course Index\n"]

    for letter, group in groupby(sorted_entries, key=lambda e: e.letter_group):
        sections.append(f"## {letter}\n")
        sections.append("| Topic / Term | Book | Page | Category | Notes / Aliases |")
        sections.append("| :--- | :--- | :--- | :--- | :--- |")

        for e in group:
            term = e.term.replace("|", "\\|")
            book = e.book.replace("|", "\\|")
            cat = e.category.replace("|", "\\|")

            notes_parts = []
            if e.notes:
                notes_parts.append(e.notes.replace("|", "\\|"))
            if e.synonyms:
                notes_parts.append(f"Aliases: {', '.join(e.synonyms)}".replace("|", "\\|"))
            notes_str = " ; ".join(notes_parts)

            sections.append(f"| {term} | {book} | {e.page} | {cat} | {notes_str} |")

        sections.append("")  # Blank line between letter groups

    return "\n".join(sections).strip() + "\n"