# SANS Indexer (`sans-indexer`)

A modular, type-safe CLI engine designed for fast study indexing, sub-second SQLite FTS5 search, and print-ready reference binder export.

---

## GIAC / SANS Index Rules

* Hardcopy Only: All materials taken into the testing center or used during proctored remote exams must be physically printed. No digital devices or soft copies are permitted.
* Allowed: Official course books, printed slides, personal notes, and custom printed indexes.
* Prohibited: Verbatim practice exam questions, brain dumps, and electronic devices.

---

## Quickstart

uv sync --all-groups
uv run pytest

---

## Basic Usage

* Add Entry:
  uv run sans-index add --term "WPA3 SAE" --book "B1" --page 142 --notes "Dragonfly handshake"

* Search:
  uv run sans-index search "Dragonfly"

* Export to HTML for Printing:
  uv run sans-index export --format html --out print_index.html