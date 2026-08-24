# SANS / GIAC Indexer (`sans-indexer`)

A fast, terminal-native indexing utility and search engine tailored for open-book certification exams (GIAC, SANS, OSCP). Built to transition study notes from manual, error-prone spreadsheets into a structured, searchable database and high-density, print-ready HTML/Markdown reference tables.

---

## Key Features

- **Interactive Study REPL:** Continuous entry mode while reading physical course materials without re-typing command flags.
- **SQLite FTS5 Full-Text Search:** Sub-millisecond BM25-ranked keyword and token search directly from the terminal.
- **Color-Coded Print Exporters:** Generates multi-column, print-optimized HTML tables with deterministic pastel badges for books and categories (`Ctrl + P` to PDF).
- **Automated Sorting & Grouping:** Natural alphanumeric sorting grouped under alphabet letter headers (`#`, `A`–`Z`).
- **Deduplicated Merging:** Merge study notes across teammates or past course runs without duplicate `(term, book, page)` rows.
- **Dynamic Course Profiles:** Switch datasets on the fly via the `SANS_INDEX_FILE` environment variable.

---

## Architecture & Design

```
sans-indexer/
├── src/sans_indexer/
│   ├── cli/             # Click CLI, commands, and Rich REPL loop
│   ├── engine/          # In-memory SQLite FTS5 index & BM25 ranker
│   ├── exporters/       # HTML & Markdown renderers with CSS print formatting
│   ├── models.py        # Pydantic v2 data models, validation & sort keys
│   └── storage/         # Flat-file CSV persistence & atomic deduplicated merging
└── tests/               # Pytest suite with CliRunner and tmp_path isolation
```

---

## Installation

Requires **Python 3.10+** and [uv](https://github.com/astral-sh/uv) (or `pip` / `pipx`).

```bash
# Clone the repository
git clone [https://github.com/DanielTolczyk/sans-indexer.git](https://github.com/DanielTolczyk/sans-indexer.git)
cd sans-indexer

# Install dependencies and register CLI entry point
uv sync
```

---

## Usage Guide

### 1. Interactive Study REPL (Recommended)
Launch the REPL when reading through course books. It prompts for your active book once and keeps a loop open for rapid logging:

```bash
uv run sans-index repl
```

```text
SANS Indexer — Interactive Study REPL
Type :q or press Ctrl+C to exit.

Active Book identifier (e.g. B1): B2

Term / Concept: Kerberoasting
Page number: 55
Category [General]: Active Directory
Notes / Syntax: Request TGS for SPN service accounts
Aliases / Synonyms (comma-separated): SPN Roasting, TGS Attack
Saved: [B2 p.55] Kerberoasting
```

---

### 2. Single-Entry Add Command
Add entries directly via CLI flags:

```bash
uv run sans-index add \
  --term "Pass-the-Hash" \
  --book "B3" \
  --page 88 \
  --cat "Lateral Movement" \
  --notes "NTLM authentication without plaintext" \
  --synonyms "PtH"
```

---

### 3. Full-Text Search
Query your indexed materials using the built-in FTS5 engine:

```bash
uv run sans-index search "kerberos"
```

---

### 4. Merging Multiple Datasets
Combine external notes or a teammate's index without introducing duplicate records:

```bash
uv run sans-index merge partner_notes.csv
```

---

### 5. Print-Ready HTML & Markdown Export
Export your dataset to print-optimized reference formats:

```bash
# Export to HTML (with color-coded badges)
uv run sans-index export --format html --out exam_index.html

# Export to Markdown table
uv run sans-index export --format md --out exam_index.md
```

---

## Multi-Course Profile Switching

By default, data is saved to `data/index.csv`. To switch targets between different certification courses, set the `SANS_INDEX_FILE` environment variable:

```bash
# Linux / macOS (Bash / Zsh)
export SANS_INDEX_FILE="data/sec504.csv"

# Windows PowerShell
$env:SANS_INDEX_FILE="data/sec504.csv"

# Windows Command Prompt
set SANS_INDEX_FILE=data/sec504.csv
```

All subsequent commands (`repl`, `add`, `search`, `export`, `merge`) will automatically use that dataset.

---

## Exam Printing Tips (HTML Export)

To get the most legible printed reference sheets for an open-book exam:

1. Open the generated `exam_index.html` file in Chrome, Edge, or Firefox.
2. Press `Ctrl + P` (or `Cmd + P` on macOS).
3. Set destination to **Save as PDF** or your physical printer.
4. Under **More Settings**:
   - **Margins:** Set to *Minimum* or *Custom (0.4 in)*.
   - **Options:** Enable **Background graphics** (ensures book and category badges print in color).
   - **Headers and Footers:** Uncheck to maximize vertical page real estate.

---

## Development & Testing

Run the full test suite:

```bash
uv run pytest -v
```

## Disclaimer

This project is an independent study utility created for educational purposes. It is not affiliated with, sponsored by, endorsed by, or associated with SANS Institute or GIAC Certifications. SANS is a registered trademark of the SANS Institute, and GIAC is a registered trademark of The Escal Institute of Advanced Technologies, Inc. 

This repository contains only software tooling and does not distribute any proprietary course books, questions, or copyrighted curriculum materials.