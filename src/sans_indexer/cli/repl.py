from __future__ import annotations

from pathlib import Path
from rich.console import Console
from rich.prompt import Prompt

from sans_indexer.models import IndexEntry
from sans_indexer.storage.csv_store import CSVStorage

console = Console()


def run_repl(file_path: Path) -> None:
    """Runs an interactive CLI loop for rapid indexing during study sessions."""
    storage = CSVStorage(file_path)
    console.print("[bold green]SANS Indexer — Interactive Study REPL[/bold green]")
    console.print("Type [bold cyan]:q[/bold cyan] or press Ctrl+C to exit.\n")

    current_book = Prompt.ask("[bold yellow]Active Book identifier (e.g. B1)[/bold yellow]")

    while True:
        try:
            term = Prompt.ask("\n[bold]Term / Concept[/bold]")
            if term.strip().lower() == ":q":
                break
            if not term.strip():
                continue

            page_str = Prompt.ask("Page number")
            if page_str.strip().lower() == ":q":
                break
            try:
                page = int(page_str.strip())
            except ValueError:
                console.print("[red]Invalid page number. Skipped.[/red]")
                continue

            category = Prompt.ask("Category", default="General")
            notes = Prompt.ask("Notes / Syntax", default="")
            synonyms_raw = Prompt.ask("Aliases / Synonyms (comma-separated)", default="")

            syn_list = [s.strip() for s in synonyms_raw.split(",") if s.strip()]

            entry = IndexEntry(
                term=term.strip(),
                book=current_book.strip(),
                page=page,
                category=category.strip(),
                notes=notes.strip(),
                synonyms=syn_list,
            )

            storage.add(entry)
            console.print(f"[green]Saved:[/green] [{entry.book} p.{entry.page}] {entry.term}")

        except (KeyboardInterrupt, EOFError):
            break

    console.print("\n[bold green]REPL session closed.[/bold green]")
    