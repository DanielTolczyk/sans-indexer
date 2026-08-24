from pathlib import Path
from click.testing import CliRunner

from sans_indexer.cli.main import cli
from sans_indexer.models import IndexEntry
from sans_indexer.storage.csv_store import CSVStorage


def test_cli_flashcards_empty(tmp_path: Path):
    runner = CliRunner()
    csv_file = str(tmp_path / "empty.csv")
    result = runner.invoke(cli, ["flashcards", "--file", csv_file])
    assert result.exit_code == 0
    assert "No entries found" in result.output


def test_cli_flashcards_with_entries(tmp_path: Path):
    runner = CliRunner()
    csv_file = str(tmp_path / "cards_test.csv")
    storage = CSVStorage(csv_file)

    storage.add(
        IndexEntry(
            term="Mimikatz",
            book="B3",
            page=42,
            category="Credential Access",
            notes="sekurlsa::logonpasswords",
            synonyms=["lsass dump"],
        )
    )

    # Press Enter to flip, then 'y' for remembered
    result = runner.invoke(
        cli,
        ["flashcards", "--file", csv_file],
        input="\ny\n",
    )
    assert result.exit_code == 0
    assert "Mimikatz" in result.output
    assert "sekurlsa::logonpasswords" in result.output
    assert "Mastered: 1/1 (100.0%)" in result.output