from sans_indexer.models import IndexEntry


def test_index_entry_creation_and_defaults():
    entry = IndexEntry(term="Kerberos", book="B1", page="10")
    assert entry.term == "Kerberos"
    assert entry.book == "B1"
    assert entry.page == "10"
    assert entry.category == "General"
    assert entry.notes == ""
    assert entry.synonyms == []
    assert entry.is_lab is False


def test_index_entry_page_spans_and_sort():
    e1 = IndexEntry(term="Kerberos", book="B1", page="10-15", category="Auth")
    e2 = IndexEntry(term="Kerberos", book="B1", page="5", category="Auth")
    e3 = IndexEntry(term="AAA Protocol", book="B1", page="100", category="Auth")

    assert e1.start_page_num == 10
    assert e2.start_page_num == 5
    assert e3.start_page_num == 100

    entries = [e1, e2, e3]
    sorted_entries = sorted(entries, key=lambda e: (e.letter_group, e.sort_key))
    
    assert sorted_entries[0].term == "AAA Protocol"
    assert sorted_entries[1].page == "5"
    assert sorted_entries[2].page == "10-15"


def test_letter_group():
    assert IndexEntry(term="Active Directory", book="B1", page="1").letter_group == "A"
    assert IndexEntry(term="1Password", book="B1", page="1").letter_group == "#"
    assert IndexEntry(term="_Underscore", book="B1", page="1").letter_group == "#"