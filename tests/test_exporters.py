from sans_indexer.exporters.html_exporter import export_to_html
from sans_indexer.exporters.markdown_exporter import export_to_markdown
from sans_indexer.models import IndexEntry


def test_markdown_export():
    entries = [
        IndexEntry(term="Kerberos", book="B1", page="10-15", category="Auth", notes="Ticket-granting auth"),
        IndexEntry(term="Pass-the-Hash", book="B2", page="20", category="Lateral Movement", synonyms=["PtH"], is_lab=True),
    ]
    md = export_to_markdown(entries)

    assert "# SANS / GIAC Open-Book Exam Index" in md
    assert "## K" in md
    assert "## P" in md
    assert "**Kerberos**" in md
    assert "`B1` p.10-15" in md
    assert "**[LAB]**" in md


def test_html_export():
    entries = [
        IndexEntry(term="BloodHound", book="B3", page="45", category="Recon", is_lab=True),
        IndexEntry(term="Responder", book="B1", page="12-14", category="Network Attacks", synonyms=["LLMNR Poisoner"]),
    ]
    html_out = export_to_html(entries)

    assert "<!DOCTYPE html>" in html_out
    assert "BloodHound" in html_out
    assert "badge-lab" in html_out
    assert "p.12-14" in html_out
    assert "Responder" in html_out