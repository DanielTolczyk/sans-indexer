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
├── pyproject.toml
├── ARCHITECTURE.md
├── README.md
├── .gitignore
├── data/                       # Local CSVs (git-ignored)
├── src/
│   └── sans_indexer/
│       ├── init.py
│       ├── models.py           # Core Pydantic data schemas
│       ├── storage/            # Local CSV & Remote fetchers
│       │   ├── base.py
│       │   ├── csv_store.py
│       │   └── remote_store.py
│       ├── engine/             # SQLite FTS5 query & ranking
│       │   ├── fts.py
│       │   └── ranker.py
│       ├── exporters/          # Multi-column HTML & Markdown renderers
│       │   ├── base.py
│       │   ├── html.py
│       │   └── markdown.py
│       └── cli/                # Click commands & Interactive REPL
│           ├── main.py
│           ├── study.py
│           └── display.py
└── tests/
├── conftest.py
├── test_models.py
├── test_storage.py
├── test_engine.py
└── test_exporters.py

## 4. Execution Phases
- **Phase 1:** Project scaffolding, `pyproject.toml`, and `models.py`.
- **Phase 2:** Storage engine (`storage/csv_store.py`).
- **Phase 3:** Search engine (`engine/fts.py`).
- **Phase 4:** Print-ready HTML & Markdown exporters (`exporters/html.py`).
- **Phase 5:** Interactive REPL and Click CLI (`cli/`).