from sans_indexer.exporters.html_exporter import export_to_html
from sans_indexer.exporters.markdown_exporter import export_to_markdown
from sans_indexer.models import IndexEntry


def test_html_export():
    entries = [
        IndexEntry(
            term="WPA3 SAE",
            book="B1",
            page=142,
            category="Wireless",
            notes="Dragonfly handshake",
            synonyms=["SAE"],
        ),
        IndexEntry(
            term="Kerberoasting",
            book="B2",
            page=55,
            category="Active Directory",
            notes="Extract TGS",
        ),
    ]

    html_out = export_to_html(entries)

    # Check for letter groups
    assert "<div class='letter-header'>K</div>" in html_out
    assert "<div class='letter-header'>W</div>" in html_out

    # Check terms and details
    assert "Kerberoasting" in html_out
    assert "WPA3 SAE" in html_out
    assert "Dragonfly handshake" in html_out
    assert "<em>Aliases:</em> SAE" in html_out


def test_markdown_export():
    entries = [
        IndexEntry(
            term="Kerberoasting",
            book="B2",
            page=55,
            category="Active Directory",
            notes="Extract TGS",
        ),
        IndexEntry(
            term="AS-REP Roasting",
            book="B2",
            page=58,
            category="Active Directory",
            notes="No preauth required",
        ),
    ]

    md_out = export_to_markdown(entries)

    # Check section headers and ordering
    assert "## A" in md_out
    assert "## K" in md_out
    assert "| AS-REP Roasting | B2 | 58 | Active Directory | No preauth required |" in md_out
    assert "| Kerberoasting | B2 | 55 | Active Directory | Extract TGS |" in md_out