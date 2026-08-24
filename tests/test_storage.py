from pathlib import Path
from sans_indexer.models import IndexEntry
from sans_indexer.storage.csv_store import CSVStorage


def test_csv_storage_add_and_load(tmp_path: Path):
    # tmp_path is a built-in pytest fixture providing a temporary directory
    csv_file = tmp_path / "test_index.csv"
    storage = CSVStorage(csv_file)

    entry1 = IndexEntry(
        term="WPA3 SAE",
        book="B1",
        page=142,
        category="Wireless",
        notes="Dragonfly handshake",
        synonyms=["Dragonfly", "SAE"],
    )
    entry2 = IndexEntry(
        term="Kerberoasting",
        book="B2",
        page=55,
        category="Active Directory",
        notes="Request TGS for SPN and crack offline",
    )

    # 1. Add entries
    storage.add(entry1)
    storage.add(entry2)

    # 2. Verify file was created
    assert csv_file.exists()

    # 3. Load entries back
    loaded = list(storage.load_all())
    assert len(loaded) == 2

    assert loaded[0].term == "WPA3 SAE"
    assert loaded[0].book == "B1"
    assert loaded[0].page == 142
    assert loaded[0].synonyms == ["Dragonfly", "SAE"]

    assert loaded[1].term == "Kerberoasting"
    assert loaded[1].page == 55


def test_csv_storage_load_nonexistent_file(tmp_path: Path):
    csv_file = tmp_path / "missing.csv"
    storage = CSVStorage(csv_file)

    loaded = list(storage.load_all())
    assert loaded == []

def test_csv_storage_merge(tmp_path: Path):
    target_file = tmp_path / "target.csv"
    source_file = tmp_path / "source.csv"

    target_store = CSVStorage(target_file)
    target_store.add(IndexEntry(term="Kerberos", book="B1", page=10, category="Auth"))

    source_store = CSVStorage(source_file)
    source_store.add(IndexEntry(term="Kerberos", book="B1", page=10, category="Auth"))  # Duplicate
    source_store.add(IndexEntry(term="NTLM", book="B1", page=20, category="Auth"))      # New

    added, skipped = target_store.merge_from(source_file)
    assert added == 1
    assert skipped == 1

    all_entries = list(target_store.load_all())
    assert len(all_entries) == 2
    assert {e.term for e in all_entries} == {"Kerberos", "NTLM"}