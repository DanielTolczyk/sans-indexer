from __future__ import annotations

from collections import Counter
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from sans_indexer.models import IndexEntry
from sans_indexer.storage.csv_store import CSVStorage

console = Console()


def show_stats(file_path: Path) -> None:
    """Calculates and displays index coverage, breakdown by book/category, and health warnings."""
    storage = CSVStorage(file_path)
    entries: list[IndexEntry] = list(storage.load_all())

    if not entries:
        console.print(f"[yellow]No entries found in {file_path}.[/yellow]")
        return

    total_entries = len(entries)
    lab_entries = sum(1 for e in entries if e.is_lab)
    books_counter = Counter(e.book for e in entries)
    categories_counter = Counter(e.category for e in entries)

    # Overview panel
    summary_text = (
        f"Total Terms: [bold cyan]{total_entries}[/bold cyan]  •  "
        f"Hands-On Lab Terms: [bold yellow]{lab_entries}[/bold yellow] ({ (lab_entries/total_entries)*100:.1f}%)  •  "
        f"Unique Books: [bold green]{len(books_counter)}[/bold green]  •  "
        f"Unique Categories: [bold magenta]{len(categories_counter)}[/bold magenta]"
    )
    console.print(Panel(summary_text, title="[bold]SANS Index Coverage Statistics[/bold]", border_style="cyan"))

    # Book Breakdown Table
    book_table = Table(title="Book Distribution & Coverage", header_style="bold blue")
    book_table.add_column("Book", style="bold")
    book_table.add_column("Count", justify="right")
    book_table.add_column("Lab Items", justify="right")
    book_table.add_column("Share", justify="right")
    book_table.add_column("Status")

    avg_per_book = total_entries / max(len(books_counter), 1)

    for book, count in sorted(books_counter.items()):
        book_labs = sum(1 for e in entries if e.book == book and e.is_lab)
        pct = (count / total_entries) * 100
        
        # Health heuristic
        if count < avg_per_book * 0.4 and len(books_counter) > 1:
            status = "[yellow]⚠️ Low coverage[/yellow]"
        else:
            status = "[green]✓ Healthy[/green]"

        book_table.add_row(book, str(count), str(book_labs), f"{pct:.1f}%", status)

    console.print(book_table)

    # Top Categories Table
    cat_table = Table(title="Top Categories", header_style="bold magenta")
    cat_table.add_column("Category", style="bold")
    cat_table.add_column("Entries", justify="right")
    cat_table.add_column("Percentage", justify="right")

    for cat, count in categories_counter.most_common(8):
        pct = (count / total_entries) * 100
        cat_table.add_row(cat, str(count), f"{pct:.1f}%")

    console.print(cat_table)