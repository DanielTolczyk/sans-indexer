import pytest
from pydantic import ValidationError
from sans_indexer.models import IndexEntry


def test_index_entry_valid():
    entry = IndexEntry(
        term="  WPA3 SAE Handshake  ",
        book=" B1 ",
        page=142,
        category=" 802.11/Crypto ",
        notes=" Dragonfly commit/confirm exchange ",
        synonyms="Dragonfly, SAE; Simultaneous Authentication",
    )
    assert entry.term == "WPA3 SAE Handshake"
    assert entry.book == "B1"
    assert entry.page == 142
    assert entry.category == "802.11/Crypto"
    assert entry.notes == "Dragonfly commit/confirm exchange"
    assert entry.synonyms == ["Dragonfly", "SAE", "Simultaneous Authentication"]
    assert entry.letter_group == "W"


def test_index_entry_invalid_page():
    with pytest.raises(ValidationError):
        IndexEntry(term="Beacon Frame", book="B1", page=0)


def test_index_entry_letter_group_symbols():
    entry = IndexEntry(term="802.11ax (Wi-Fi 6)", book="B1", page=22)
    assert entry.letter_group == "#"