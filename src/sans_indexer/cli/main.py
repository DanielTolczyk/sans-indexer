from __future__ import annotations

from pathlib import Path
import click

from sans_indexer.cli.repl import run_repl
from sans_indexer.engine.search import SearchEngine
from sans_indexer.exporters.html_exporter import export_to_html
from sans_indexer.exporters.markdown_exporter import export_to_markdown
from sans_indexer.models import IndexEntry
from sans_indexer.storage.csv_store import CSVStorage

DEFAULT_DATA_PATH = Path("data/index.csv")


@click.group()
def cli() -> None:
    """SANS/GIAC Course Material Indexer CLI."""
    pass


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
    """Launch an interactive study REPL session for rapid entry."""
    run_repl(Path(file))


@cli.command()
@click.option("--term", "-t", required=True, help="Topic or concept term.")
@click.option("--book", "-b", required=True, help="Course book identifier (e.g. B1).")
@click.option("--page", "-p", required=True, type=int, help="Page number.")
@click.option("--cat", "-c", default="General", help="Category (default: General).")
@click.option("--notes", "-n", default="", help="Short notes, flags, or syntax reminders.")
@click.option("--synonyms", "-s", default="", help="Comma-separated synonyms or aliases.")
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
    page: int,
    cat: str,
    notes: str,
    synonyms: str,
    file: str | Path,
) -> None:
    """Add a new index entry to the dataset."""
    storage = CSVStorage(file)
    syn_list = [s.strip() for s in synonyms.split(",") if s.strip()]

    entry = IndexEntry(
        term=term,
        book=book,
        page=page,
        category=cat,
        notes=notes,
        synonyms=syn_list,
    )
    storage.add(entry)
    click.echo(f"Added: [{entry.book} p.{entry.page}] {entry.term}")


@cli.command()
@click.argument("query")
@click.option(
    "--file",
    "-f",
    default=DEFAULT_DATA_PATH,
    envvar="SANS_INDEX_FILE",
    type=click.Path(),
    help="Source CSV file (or set SANS_INDEX_FILE).",
)
@click.option("--limit", "-l", default=10, type=int, help="Max number of results to display.")
def search(query: str, file: str | Path, limit: int) -> None:
    """Perform a ranked FTS5 search on indexed entries."""
    storage = CSVStorage(file)
    entries = list(storage.load_all())

    if not entries:
        click.echo(f"No index records found in {file}.")
        return

    engine = SearchEngine()
    engine.index_entries(entries)
    results = engine.search(query, limit=limit)
    engine.close()

    if not results:
        click.echo(f"No matches found for '{query}'.")
        return

    click.echo(f"\nFound {len(results)} match(es):\n")
    for r in results:
        e = r.entry
        syn_str = f" | Aliases: {', '.join(e.synonyms)}" if e.synonyms else ""
        click.echo(f"  * {e.term:<28} [{e.book} p.{e.page}] ({e.category})")
        if e.notes or syn_str:
            click.echo(f"    Notes: {e.notes}{syn_str}")


@cli.command()
@click.option(
    "--format",
    "-m",
    "export_format",
    type=click.Choice(["html", "md"], case_sensitive=False),
    default="html",
    help="Export file format.",
)
@click.option("--out", "-o", required=True, type=click.Path(), help="Output file path.")
@click.option(
    "--file",
    "-f",
    default=DEFAULT_DATA_PATH,
    envvar="SANS_INDEX_FILE",
    type=click.Path(),
    help="Source CSV file (or set SANS_INDEX_FILE).",
)
def export(export_format: str, out: str | Path, file: str | Path) -> None:
    """Export index to print-optimized HTML or Markdown."""
    storage = CSVStorage(file)
    entries = list(storage.load_all())

    if not entries:
        click.echo(f"No index records found in {file} to export.")
        return

    out_path = Path(out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    if export_format.lower() == "html":
        content = export_to_html(entries)
    else:
        content = export_to_markdown(entries)

    out_path.write_text(content, encoding="utf-8")
    click.echo(f"Exported {len(entries)} entries to {out_path} ({export_format.upper()})")


if __name__ == "__main__":
    cli()