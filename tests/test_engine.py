import pytest
from sans_indexer.engine.search import SearchEngine
from sans_indexer.models import IndexEntry


@pytest.fixture
def sample_entries() -> list[IndexEntry]:
    return [
        IndexEntry(
            term="WPA3 SAE",
            book="B1",
            page=142,
            category="Wireless",
            notes="Simultaneous Authentication of Equals; replaces PSK",
            synonyms=["Dragonfly", "SAE"],
        ),
        IndexEntry(
            term="Kerberoasting",
            book="B2",
            page=55,
            category="Active Directory",
            notes="Request TGS for service principal names",
            synonyms=["TGS-REQ", "SPN crack"],
        ),
        IndexEntry(
            term="AS-REP Roasting",
            book="B2",
            page=58,
            category="Active Directory",
            notes="Targets accounts with DONT_REQ_PREAUTH set",
            synonyms=["Pre-authentication"],
        ),
    ]


def test_search_exact_and_prefix(sample_entries: list[IndexEntry]):
    engine = SearchEngine()
    engine.index_entries(sample_entries)

    # Prefix match
    results = engine.search("kerb")
    assert len(results) == 1
    assert results[0].entry.term == "Kerberoasting"

    # Exact term match
    results_exact = engine.search("WPA3")
    assert len(results_exact) == 1
    assert results_exact[0].entry.term == "WPA3 SAE"

    engine.close()


def test_search_synonyms_and_notes(sample_entries: list[IndexEntry]):
    engine = SearchEngine()
    engine.index_entries(sample_entries)

    # Match by synonym
    results = engine.search("Dragonfly")
    assert len(results) == 1
    assert results[0].entry.term == "WPA3 SAE"

    # Match in notes
    results_notes = engine.search("DONT_REQ_PREAUTH")
    assert len(results_notes) == 1
    assert results_notes[0].entry.term == "AS-REP Roasting"

    engine.close()


def test_search_empty_query(sample_entries: list[IndexEntry]):
    engine = SearchEngine()
    engine.index_entries(sample_entries)

    assert engine.search("") == []
    assert engine.search("   ") == []

    engine.close()
    