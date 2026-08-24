from pathlib import Path
from click.testing import CliRunner

from sans_indexer.cli.main import cli


def test_cli_add_and_search(tmp_path: Path):
    runner = CliRunner()
    csv_file = str(tmp_path / "test_cli_index.csv")

    # 1. Test 'add' command
    add_result = runner.invoke(
        cli,
        [
            "add",
            "--term", "Pass-the-Hash",
            "--book", "B3",
            "--page", "88",
            "--cat", "Lateral Movement",
            "--notes", "NTLM hash authentication without plaintext",
            "--synonyms", "PtH",
            "--file", csv_file,
        ],
    )
    assert add_result.exit_code == 0
    assert "Added: [B3 p.88] Pass-the-Hash" in add_result.output

    # 2. Test 'search' command
    search_result = runner.invoke(
        cli,
        ["search", "Pass", "--file", csv_file],
    )
    assert search_result.exit_code == 0
    assert "Pass-the-Hash" in search_result.output
    assert "[B3 p.88]" in search_result.output


def test_cli_export(tmp_path: Path):
    runner = CliRunner()
    csv_file = str(tmp_path / "test_cli_index.csv")
    out_html = str(tmp_path / "output.html")

    # Add a sample record first
    runner.invoke(
        cli,
        [
            "add",
            "-t", "BloodHound",
            "-b", "B4",
            "-p", "12",
            "-c", "AD Enumeration",
            "-f", csv_file,
        ],
    )

    # Export to HTML
    export_result = runner.invoke(
        cli,
        ["export", "--format", "html", "--out", out_html, "--file", csv_file],
    )
    assert export_result.exit_code == 0
    assert Path(out_html).exists()
    assert "BloodHound" in Path(out_html).read_text(encoding="utf-8")