from __future__ import annotations

import html
from itertools import groupby
from typing import Iterable

from sans_indexer.models import IndexEntry

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>SANS Open-Book Reference Index</title>
  <style>
    @page {{
      size: letter portrait;
      margin: 0.5in;
    }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      font-size: 9pt;
      line-height: 1.25;
      color: #111;
      margin: 0;
    }}
    h1 {{
      font-size: 14pt;
      margin: 0 0 8px 0;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }}
    .letter-header {{
      background-color: #222;
      color: #fff;
      font-weight: bold;
      font-size: 11pt;
      padding: 3px 6px;
      margin-top: 12px;
      margin-bottom: 4px;
      border-radius: 2px;
      page-break-after: avoid;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      margin-bottom: 8px;
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
      font-size: 8.5pt;
      text-transform: uppercase;
    }}
    td {{
      padding: 3px 4px;
      border-bottom: 0.5px solid #ddd;
      vertical-align: top;
    }}
    .col-term {{ width: 26%; font-weight: 600; }}
    .col-loc  {{ width: 12%; white-space: nowrap; }}
    .col-cat  {{ width: 18%; color: #444; }}
    .col-notes {{ width: 44%; color: #222; }}
    .badge {{
      font-weight: bold;
      color: #000;
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
    """Renders sorted entries into a print-optimized HTML document."""
    sorted_entries = sorted(entries, key=lambda e: (e.letter_group, e.sort_key))
    sections: list[str] = []

    for letter, group in groupby(sorted_entries, key=lambda e: e.letter_group):
        rows: list[str] = []
        for e in group:
            term = html.escape(e.term)
            loc = f"<span class='badge'>{html.escape(e.book)}</span> p.{e.page}"
            cat = html.escape(e.category)
            
            notes_parts = []
            if e.notes:
                notes_parts.append(html.escape(e.notes))
            if e.synonyms:
                syn_str = f"<em>Aliases:</em> {html.escape(', '.join(e.synonyms))}"
                notes_parts.append(syn_str)
            notes_html = " | ".join(notes_parts)

            rows.append(
                f"<tr>"
                f"<td class='col-term'>{term}</td>"
                f"<td class='col-loc'>{loc}</td>"
                f"<td class='col-cat'>{cat}</td>"
                f"<td class='col-notes'>{notes_html}</td>"
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