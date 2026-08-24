from __future__ import annotations

import random
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

from sans_indexer.models import IndexEntry
from sans_indexer.storage.csv_store import CSVStorage

console = Console()


def run_flashcards(
    file_path: Path,
    category: str | None = None,
    book: str | None = None,
    limit: int | None = None,
    shuffle: bool = True,
) -> None:
    """Runs an interactive terminal flashcard review session for active recall."""
    storage = CSVStorage(file_path)
    entries: list[IndexEntry] = list(storage.load_all())

    if not entries:
        console.print(f"[yellow]No entries found in {file_path}.[/yellow]")
        return

    # Filter by category or book if requested
    if category:
        entries = [e for e in entries if e.category.strip().lower() == category.strip().lower()]
    if book:
        entries = [e for e in entries if e.book.strip().lower() == book.strip().lower()]

    if not entries:
        console.print("[yellow]No entries matched your filter criteria.[/yellow]")
        return

    if shuffle:
        random.shuffle(entries)

    if limit and limit > 0:
        entries = entries[:limit]

    total = len(entries)
    known = 0
    reviewed = 0

    console.print("\n[bold green]SANS Indexer — Active Recall Flashcards[/bold green]")
    console.print(f"Loaded [bold cyan]{total}[/bold cyan] card(s). Type [bold cyan]:q[/bold cyan] at any prompt to exit.\n")

    for idx, entry in enumerate(entries, start=1):
        console.rule(f"Card {idx}/{total} • [{entry.book} p.{entry.page}]")

        # Front of card (Prompt / Term)
        console.print(
            Panel(
                f"[bold white]{entry.term}[/bold white]\n\n"
                f"[dim]Category:[/dim] {entry.category}",
                title="[bold yellow]Front[/bold yellow]",
                border_style="yellow",
            )
        )

        response = Prompt.ask("Press [bold]Enter[/bold] to flip card (or :q to quit)", default="")
        if response.strip().lower() == ":q":
            break

        # Back of card (Details / Notes / Location)
        notes_text = entry.notes if entry.notes else "[italic dim]No notes recorded[/italic dim]"
        alias_text = f"\n[dim]Aliases:[/dim] {', '.join(entry.synonyms)}" if entry.synonyms else ""

        console.print(
            Panel(
                f"[bold green]Notes / Syntax:[/bold green]\n{notes_text}{alias_text}\n\n"
                f"[dim]Reference Location:[/dim] [bold]{entry.book} page {entry.page}[/bold]",
                title="[bold green]Back[/bold green]",
                border_style="green",
            )
        )

        feedback = Prompt.ask(
            "Did you know this? ([green]y[/green]/[red]n[/red])",
            choices=["y", "n", ":q"],
            default="y",
        )
        if feedback == ":q":
            break

        reviewed += 1
        if feedback == "y":
            known += 1

    # Session Summary
    console.print("\n" + "=" * 40)
    console.print("[bold cyan]Flashcard Session Summary[/bold cyan]")
    if reviewed > 0:
        pct = (known / reviewed) * 100
        console.print(f"Reviewed: [bold]{reviewed}[/bold] / {total}")
        console.print(f"Mastered: [bold]{known}/{reviewed}[/bold] ([bold green]{pct:.1f}%[/bold green])")
    else:
        console.print("No cards reviewed.")
    console.print("=" * 40 + "\n")