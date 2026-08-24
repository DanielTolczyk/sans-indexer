# SANS Indexer: Architecture & Technical Design

## 1. Overview
A modular, type-safe CLI engine designed for fast study indexing, sub-second SQLite FTS5 search, and print-ready physical binder export.

## 2. Core Principles
- **Separation of Concerns:** Storage I/O, search ranking, and presentation/exporting live in independent modules.
- **Data Portability:** Local CSV is the single source of truth; compatible with published Google Sheets.
- **Low-Friction Study Workflow:** Supports both direct CLI flags and an interactive REPL study prompt that retains active book state.
- **Strict Typing:** All records validated via Pydantic models.

## 3. Directory Layout
sans-indexer/
├── src/sans_indexer/
│   ├── cli/             # Click CLI commands, REPL loop, and Rich flashcards review
│   │   ├── flashcards.py
│   │   ├── main.py
│   │   └── repl.py
│   ├── engine/          # In-memory SQLite FTS5 index & BM25 ranker
│   │   └── search.py
│   ├── exporters/       # HTML & Markdown renderers with CSS print formatting
│   │   ├── html_exporter.py
│   │   └── markdown_exporter.py
│   ├── models.py        # Pydantic v2 data models, validation & sort keys
│   └── storage/         # Flat-file CSV persistence & atomic deduplicated merging
│       └── csv_store.py
└── tests/               # Pytest suite with CliRunner and tmp_path isolation
├── test_cli.py
├── test_engine.py
├── test_exporters.py
├── test_flashcards.py
├── test_models.py
├── test_repl.py
└── test_storage.py

