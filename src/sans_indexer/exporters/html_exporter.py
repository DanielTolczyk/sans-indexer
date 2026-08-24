from __future__ import annotations

import hashlib
import html
from itertools import groupby
from typing import Iterable

from sans_indexer.models import IndexEntry

# Muted, print-friendly pastel palette (light background, darker text/border)
COLOR_PALETTE = [
    {"bg": "#E8F0FE", "text": "#174EA6", "border": "#AECBFA"},  # Blue
    {"bg": "#FEF7E0", "text": "#B06000", "border": "#FDD663"},  # Yellow / Amber
    {"bg": "#E6F4EA", "text": "#137333", "border": "#CEEAD6"},  # Green
    {"bg": "#FCE8E6", "text": "#C5221F", "border": "#FAD2CF"},  # Red
    {"bg": "#F3E8FD", "text": "#7627BB", "border": "#D7AEFB"},  # Purple
    {"bg": "#E0F2F1", "text": "#00695C", "border": "#80CBC4"},  # Teal
    {"bg": "#FFF0F5", "text": "#880E4F", "border": "#F48FB1"},  # Pink / Magenta
    {"bg": "#EFEBE9", "text": "#4E342E", "border": "#BCAAA4"},  # Brown
]


def _get_color(label: str) -> dict[str, str]:
    """Deterministically maps any label string to a consistent palette color."""
    if not label:
        return {"bg": "#F1F3F4", "text": "#3C4043", "border": "#DADCE0"}
    idx = int(hashlib.md5(label.encode("utf-8")).hexdigest(), 16) % len(COLOR_PALETTE)
    return COLOR_PALETTE[idx]


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>SANS / GIAC Open-Book Exam Index</title>
  <style>
    @page {{
      size: letter portrait;
      margin: 0.4in;
    }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      font-size: 8.5pt;
      line-height: 1.25;
      color: #111;
      margin: 0;
      -webkit-print-color-adjust: exact;
      print-color-adjust: exact;
    }}
    h1 {{
      font-size: 13pt;
      margin: 0 0 6px 0;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }}
    .letter-header {{
      background-color: #1a202c;
      color: #ffffff;
      font-weight: 700;
      font-size: 10pt;
      padding: 3px 6px;
      margin-top: 10px;
      margin-bottom: 3px;
      border-radius: 3px;
      page-break-after: avoid;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      margin-bottom: 6px;
    }}
    thead {{
      display: table-header-group;
    }}
    tr {{
      page-break-inside: avoid;
    }}
    th {{
      text-align: left;
      border-bottom: 1.5px solid #222;
      padding: 3px 4px;
      font-size: 8pt;
      text-transform: uppercase;
      letter-spacing: 0.3px;
    }}
    td {{
      padding: 3px 4px;
      border-bottom: 0.5px solid #e0e0e0;
      vertical-align: middle;
    }}
    .col-term {{ width: 25%; font-weight: 600; color: #111; }}
    .col-loc  {{ width: 14%; white-space: nowrap; }}
    .col-cat  {{ width: 18%; }}
    .col-notes {{ width: 43%; color: #222; }}
    
    .badge {{
      display: inline-block;
      padding: 1px 5px;
      font-size: 7.5pt;
      font-weight: 700;
      border-radius: 3px;
      border: 1px solid transparent;
      text-transform: uppercase;
      letter-spacing: 0.2px;
    }}
    .page-num {{
      font-weight: 700;
      color: #222;
      margin-left: 2px;
    }}
    .alias {{
      color: #4a5568;
      font-style: italic;
    }}
  </style>
</head>
<body>
  <h1>Course Index</h1>
  {content}
</body>
</html>
"""


def export_to_html(entries: Iterable[IndexEntry]) -> str:
    """Renders sorted entries into a print-optimized HTML document with color-coded tags."""
    sorted_entries = sorted(entries, key=lambda e: (e.letter_group, e.sort_key))
    sections: list[str] = []

    for letter, group in groupby(sorted_entries, key=lambda e: e.letter_group):
        rows: list[str] = []
        for e in group:
            term = html.escape(e.term)
            
            # Deterministic color badges for Book and Category
            book_col = _get_color(e.book)
            cat_col = _get_color(e.category)

            book_badge = (
                f"<span class='badge' style='background-color:{book_col['bg']}; "
                f"color:{book_col['text']}; border-color:{book_col['border']};'>"
                f"{html.escape(e.book)}</span>"
            )
            loc = f"{book_badge} <span class='page-num'>p.{e.page}</span>"

            cat_badge = (
                f"<span class='badge' style='background-color:{cat_col['bg']}; "
                f"color:{cat_col['text']}; border-color:{cat_col['border']};'>"
                f"{html.escape(e.category)}</span>"
            )

            notes_parts = []
            if e.notes:
                notes_parts.append(html.escape(e.notes))
            if e.synonyms:
                syn_str = f"<span class='alias'>Aliases: {html.escape(', '.join(e.synonyms))}</span>"
                notes_parts.append(syn_str)
            notes_html = " &bull; ".join(notes_parts)

            rows.append(
                f"<tr>\n"
                f"  <td class='col-term'>{term}</td>\n"
                f"  <td class='col-loc'>{loc}</td>\n"
                f"  <td class='col-cat'>{cat_badge}</td>\n"
                f"  <td class='col-notes'>{notes_html}</td>\n"
                f"</tr>"
            )

        section_html = (
            f"<div class='letter-header'>{letter}</div>\n"
            f"<table>\n"
            f"  <thead>\n"
            f"    <tr>\n"
            f"      <th class='col-term'>Topic / Term</th>\n"
            f"      <th class='col-loc'>Location</th>\n"
            f"      <th class='col-cat'>Category</th>\n"
            f"      <th class='col-notes'>Notes & Aliases</th>\n"
            f"    </tr>\n"
            f"  </thead>\n"
            f"  <tbody>\n"
            f"    {''.join(rows)}\n"
            f"  </tbody>\n"
            f"</table>"
        )
        sections.append(section_html)

    return HTML_TEMPLATE.format(content="\n".join(sections))