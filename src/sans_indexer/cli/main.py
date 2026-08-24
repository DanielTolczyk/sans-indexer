from __future__ import annotations

from pathlib import Path
import click
from rich.console import Console
from rich.table import Table

from sans_indexer.cli.flashcards import run_flashcards
from sans_indexer.cli.repl import start_repl
from sans_indexer.cli.stats import show_stats
from sans_indexer.engine.search import SearchEngine
from sans_indexer.exporters.html_exporter import export_to_html
from sans_indexer.exporters.markdown_exporter import export_to_markdown
from sans_indexer.models import IndexEntry
from sans_indexer.storage.csv_store import CSVStorage

console = Console()
DEFAULT_DATA_PATH = Path("data/index.csv")


@click.group()
def cli() -> None:
    """SANS / GIAC Exam Indexing and Search Engine."""
    pass


@cli.command()
@click.option("--term", "-t", required=True, help="Concept, command, or topic name.")
@click.option("--book", "-b", required=True, help="Book identifier (e.g. B1, B2).")
@click.option("--page", "-p", required=True, help="Page number or range (e.g. 45 or 45-48).")
@click.option("--cat", "-c", default="General", help="Subject category.")
@click.option("--notes", "-n", default="", help="Quick syntax or summary notes.")
@click.option("--synonyms", "-s", default="", help="Comma-separated aliases or acronyms.")
@click.option("--lab", "-l", is_flag=True, default=False, help="Flag entry as a hands-on lab exercise.")
@click.option(
    "--file",
    "-f",
    default=DEFAULT_DATA_PATH,
    envvar="SANS_INDEX_FILE",
    type=click.Path(),
    help="Target CSV file (or set SANS_INDEX_FILE).",
)
def add(
    term: str,
    book: str,
    page: str,
    cat: str,
    notes: str,
    synonyms: str,
    lab: bool,
    file: str | Path,
) -> None:
    """Add a new index entry."""
    storage = CSVStorage(file)
    syn_list = [s.strip() for s in synonyms.split(",") if s.strip()]
    entry = IndexEntry(
        term=term,
        book=book,
        page=page,
        category=cat,
        notes=notes,
        synonyms=syn_list,
        is_lab=lab,
    )
    storage.add(entry)
    lab_str = " [LAB]" if lab else ""
    console.print(f"[green]Added:[/green] [{entry.book} p.{entry.page}]{lab_str} [bold]{entry.term}[/bold]")


@cli.command()
@click.argument("query")
@click.option(
    "--file",
    "-f",
    default=DEFAULT_DATA_PATH,
    envvar="SANS_INDEX_FILE",
    type=click.Path(exists=True),
    help="Source CSV file (or set SANS_INDEX_FILE).",
)
def search(query: str, file: str | Path) -> None:
    """Full-text search indexed terms and syntax."""
    storage = CSVStorage(file)
    entries = list(storage.load_all())
    engine = SearchEngine(entries)
    results = engine.search(query)

    if not results:
        console.print(f"[yellow]No results found for query:[/yellow] '{query}'")
        return

    table = Table(title=f"Search Results for '{query}'", header_style="bold magenta")
    table.add_column("Term", style="bold cyan")
    table.add_column("Location", style="green")
    table.add_column("Category", style="blue")
    table.add_column("Notes / Synonyms")

    for res in results:
        entry = res.entry
        loc = f"{entry.book} p.{entry.page}"
        if entry.is_lab:
            loc += " [yellow][LAB][/yellow]"
        extra = []
        if entry.notes:
            extra.append(entry.notes)
        if entry.synonyms:
            extra.append(f"[dim]Aliases:[/dim] {', '.join(entry.synonyms)}")
        table.add_row(entry.term, loc, entry.category, " • ".join(extra))

    console.print(table)


@cli.command()
@click.option(
    "--file",
    "-f",
    default=DEFAULT_DATA_PATH,
    envvar="SANS_INDEX_FILE",
    type=click.Path(),
    help="Target CSV file (or set SANS_INDEX_FILE).",
)
def repl(file: str | Path) -> None:
    """Start interactive study REPL."""
    start_repl(Path(file))


@cli.command()
@click.option("--format", "-m", "fmt", type=click.Choice(["html", "md"]), default="html")
@click.option("--out", "-o", default=None, help="Output file path.")
@click.option(
    "--file",
    "-f",
    default=DEFAULT_DATA_PATH,
    envvar="SANS_INDEX_FILE",
    type=click.Path(exists=True),
    help="Source CSV file (or set SANS_INDEX_FILE).",
)
def export(fmt: str, out: str | None, file: str | Path) -> None:
    """Export index to HTML or Markdown."""
    storage = CSVStorage(file)
    entries = list(storage.load_all())

    if fmt == "html":
        output = export_to_html(entries)
        default_out = "index.html"
    else:
        output = export_to_markdown(entries)
        default_out = "index.md"

    out_path = Path(out) if out else Path(default_out)
    out_path.write_text(output, encoding="utf-8")
    console.print(f"[green]Successfully exported {len(entries)} entries to {out_path}[/green]")


@cli.command()
@click.argument("source_file", type=click.Path(exists=True))
@click.option(
    "--file",
    "-f",
    default=DEFAULT_DATA_PATH,
    envvar="SANS_INDEX_FILE",
    type=click.Path(),
    help="Target CSV file (or set SANS_INDEX_FILE).",
)
def merge(source_file: str, file: str | Path) -> None:
    """Merge entries from another CSV file, skipping duplicates."""
    target_storage = CSVStorage(file)
    added, skipped = target_storage.merge_from(source_file)
    click.echo(f"Merge complete: {added} new entry/entries added, {skipped} duplicate(s) skipped.")


@cli.command()
@click.option("--cat", "-c", default=None, help="Filter flashcards by category.")
@click.option("--book", "-b", default=None, help="Filter flashcards by book identifier.")
@click.option("--limit", "-l", default=None, type=int, help="Maximum number of cards to review.")
@click.option(
    "--file",
    "-f",
    default=DEFAULT_DATA_PATH,
    envvar="SANS_INDEX_FILE",
    type=click.Path(),
    help="Source CSV file (or set SANS_INDEX_FILE).",
)
def flashcards(cat: str | None, book: str | None, limit: int | None, file: str | Path) -> None:
    """Launch interactive flashcards session."""
    run_flashcards(file_path=Path(file), category=cat, book=book, limit=limit)


@cli.command()
@click.option(
    "--file",
    "-f",
    default=DEFAULT_DATA_PATH,
    envvar="SANS_INDEX_FILE",
    type=click.Path(exists=True),
    help="Source CSV file (or set SANS_INDEX_FILE).",
)
def stats(file: str | Path) -> None:
    """View index coverage stats and book distribution."""
    show_stats(Path(file))