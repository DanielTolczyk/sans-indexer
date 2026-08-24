from __future__ import annotations

from pathlib import Path
from rich.console import Console
from rich.prompt import Confirm, Prompt

from sans_indexer.models import IndexEntry
from sans_indexer.storage.csv_store import CSVStorage

console = Console()


def start_repl(file_path: Path) -> None:
    """Continuous REPL for rapid study note capture."""
    storage = CSVStorage(file_path)
    console.print("\n[bold green]SANS Indexer — Interactive Study REPL[/bold green]")
    console.print("Type [bold cyan]:q[/bold cyan] or press [bold cyan]Ctrl+C[/bold cyan] to exit.\n")

    active_book = Prompt.ask("Active Book identifier (e.g. B1, Lab 2)").strip()
    if not active_book or active_book == ":q":
        return

    active_category = "General"

    while True:
        try:
            term = Prompt.ask("\n[bold]Term / Concept[/bold]").strip()
            if term.lower() == ":q":
                break
            if not term:
                continue

            page = Prompt.ask("Page number or span (e.g. 45 or 45-48)").strip()
            if page.lower() == ":q":
                break

            category = Prompt.ask("Category", default=active_category).strip()
            if category.lower() == ":q":
                break
            active_category = category

            notes = Prompt.ask("Notes / Syntax (optional)", default="").strip()
            if notes.lower() == ":q":
                break

            synonyms_raw = Prompt.ask("Aliases / Synonyms (comma-separated, optional)", default="").strip()
            if synonyms_raw.lower() == ":q":
                break
            synonyms = [s.strip() for s in synonyms_raw.split(",") if s.strip()]

            is_lab = Confirm.ask("Is this a hands-on Lab exercise?", default=False)

            entry = IndexEntry(
                term=term,
                book=active_book,
                page=page,
                category=category,
                notes=notes,
                synonyms=synonyms,
                is_lab=is_lab,
            )
            storage.add(entry)

            lab_tag = " [bold yellow][LAB][/bold yellow]" if is_lab else ""
            console.print(f"[green]Saved:[/green] [{active_book} p.{page}]{lab_tag} [bold]{term}[/bold]")

        except (KeyboardInterrupt, EOFError):
            console.print("\n[yellow]Exiting REPL session.[/yellow]")
            break