from __future__ import annotations

from itertools import groupby
from typing import Iterable

from sans_indexer.models import IndexEntry


def export_to_markdown(entries: Iterable[IndexEntry]) -> str:
    sorted_entries = sorted(entries, key=lambda e: (e.letter_group, e.sort_key))
    lines: list[str] = ["# SANS / GIAC Open-Book Exam Index\n"]

    for letter, group in groupby(sorted_entries, key=lambda e: e.letter_group):
        lines.append(f"## {letter}\n")
        lines.append("| Topic / Term | Location | Category | Notes & Aliases |")
        lines.append("| :--- | :--- | :--- | :--- |")

        for e in group:
            loc = f"`{e.book}` p.{e.page}"
            if e.is_lab:
                loc += " **[LAB]**"

            notes_parts = []
            if e.notes:
                notes_parts.append(e.notes)
            if e.synonyms:
                notes_parts.append(f"*Aliases:* {', '.join(e.synonyms)}")
            notes_text = " • ".join(notes_parts)

            clean_term = e.term.replace("|", "\\|")
            clean_notes = notes_text.replace("|", "\\|")
            lines.append(f"| **{clean_term}** | {loc} | {e.category} | {clean_notes} |")

        lines.append("")

    return "\n".join(lines)