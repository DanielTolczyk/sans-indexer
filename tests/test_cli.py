from pathlib import Path
from click.testing import CliRunner

from sans_indexer.cli.main import cli
from sans_indexer.models import IndexEntry
from sans_indexer.storage.csv_store import CSVStorage


def test_cli_add_and_search(tmp_path: Path):
    runner = CliRunner()
    csv_file = str(tmp_path / "test.csv")

    add_res = runner.invoke(
        cli,
        [
            "add",
            "-t", "Silver Ticket",
            "-b", "B2",
            "-p", "88-92",
            "-c", "Active Directory",
            "-n", "Forged TGS service ticket",
            "-s", "TGS Forge",
            "-l",
            "-f", csv_file,
        ],
    )
    assert add_res.exit_code == 0
    assert "Added: [B2 p.88-92] [LAB] Silver Ticket" in add_res.output

    search_res = runner.invoke(cli, ["search", "forged", "-f", csv_file])
    assert search_res.exit_code == 0
    assert "Silver Ticket" in search_res.output
    assert "B2 p.88-92" in search_res.output
    assert "[LAB]" in search_res.output


def test_cli_export(tmp_path: Path):
    runner = CliRunner()
    csv_file = str(tmp_path / "test.csv")
    out_html = str(tmp_path / "out.html")

    runner.invoke(cli, ["add", "-t", "SAML", "-b", "B1", "-p", "5-8", "-f", csv_file])

    export_res = runner.invoke(cli, ["export", "--format", "html", "-o", out_html, "-f", csv_file])
    assert export_res.exit_code == 0
    assert Path(out_html).exists()
    assert "SAML" in Path(out_html).read_text(encoding="utf-8")


def test_cli_merge(tmp_path: Path):
    runner = CliRunner()
    target_csv = str(tmp_path / "target.csv")
    source_csv = str(tmp_path / "source.csv")

    runner.invoke(cli, ["add", "-t", "SAML", "-b", "B1", "-p", "5", "-f", target_csv])
    runner.invoke(cli, ["add", "-t", "SAML", "-b", "B1", "-p", "5", "-f", source_csv])
    runner.invoke(cli, ["add", "-t", "OAuth", "-b", "B1", "-p", "15-18", "-l", "-f", source_csv])

    merge_result = runner.invoke(cli, ["merge", source_csv, "--file", target_csv])
    assert merge_result.exit_code == 0
    assert "1 new entry/entries added" in merge_result.output
    assert "1 duplicate(s) skipped" in merge_result.output


def test_cli_stats(tmp_path: Path):
    runner = CliRunner()
    csv_file = str(tmp_path / "stats_test.csv")

    runner.invoke(cli, ["add", "-t", "Nmap", "-b", "B1", "-p", "12-15", "-l", "-f", csv_file])
    runner.invoke(cli, ["add", "-t", "Wireshark", "-b", "B1", "-p", "30", "-f", csv_file])

    stats_res = runner.invoke(cli, ["stats", "-f", csv_file])
    assert stats_res.exit_code == 0
    assert "Total Terms: 2" in stats_res.output
    assert "Hands-On Lab Terms: 1" in stats_res.output