from pathlib import Path
from sans_indexer.models import IndexEntry
from sans_indexer.storage.csv_store import CSVStorage


def test_csv_storage_add_and_load(tmp_path: Path):
    file_path = tmp_path / "test.csv"
    storage = CSVStorage(file_path)

    entry1 = IndexEntry(
        term="Kerberoasting",
        book="B2",
        page="55-60",
        category="Active Directory",
        notes="Request TGS for SPN service accounts",
        synonyms=["SPN Roasting", "TGS Attack"],
        is_lab=True,
    )
    entry2 = IndexEntry(
        term="Golden Ticket",
        book="B2",
        page="70",
        category="Active Directory",
    )

    storage.add(entry1)
    storage.add(entry2)

    loaded = list(storage.load_all())
    assert len(loaded) == 2
    assert loaded[0].term == "Kerberoasting"
    assert loaded[0].page == "55-60"
    assert loaded[0].is_lab is True
    assert loaded[0].synonyms == ["SPN Roasting", "TGS Attack"]
    assert loaded[1].term == "Golden Ticket"
    assert loaded[1].is_lab is False


def test_csv_storage_merge(tmp_path: Path):
    target_file = tmp_path / "target.csv"
    source_file = tmp_path / "source.csv"

    target_store = CSVStorage(target_file)
    target_store.add(IndexEntry(term="Kerberos", book="B1", page="10", category="Auth"))

    source_store = CSVStorage(source_file)
    source_store.add(IndexEntry(term="Kerberos", book="B1", page="10", category="Auth"))  # Duplicate
    source_store.add(IndexEntry(term="NTLM", book="B1", page="20-22", category="Auth", is_lab=True))  # New

    added, skipped = target_store.merge_from(source_file)
    assert added == 1
    assert skipped == 1

    all_entries = list(target_store.load_all())
    assert len(all_entries) == 2
    assert {e.term for e in all_entries} == {"Kerberos", "NTLM"}