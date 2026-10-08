import importlib.util
from pathlib import Path

import pytest

SCRIPT_PATH = Path(__file__).resolve().parent.parent / "scripts" / "search_resources.py"
spec = importlib.util.spec_from_file_location("search_resources", SCRIPT_PATH)
search_resources = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
spec.loader.exec_module(search_resources)  # type: ignore[union-attr]

DEFAULT_README = search_resources.DEFAULT_README
is_no_card = search_resources.is_no_card
parse_catalog = search_resources.parse_catalog
search_entries = search_resources.search_entries


def test_catalog_file_exists():
    assert DEFAULT_README.is_file(), f"Catalog not found at {DEFAULT_README}"


def test_parse_catalog():
    entries, category_map = parse_catalog(DEFAULT_README)
    assert len(entries) > 1000
    assert len(category_map) >= 50
    assert "Major Cloud Providers" in category_map
    assert "PaaS" in category_map
    assert "Managed Data Services" in category_map


def test_search_entries_by_keyword():
    entries, _ = parse_catalog(DEFAULT_README)
    results = search_entries(entries, query="postgres")
    assert len(results) > 0
    # Every result should contain postgres in name, desc, category, or sub_items
    for r in results:
        combined = (
            r["name"]
            + " "
            + r["category"]
            + " "
            + r["description"]
            + " "
            + " ".join(r.get("sub_items", []))
        ).lower()
        assert "postgres" in combined


def test_search_entries_by_category():
    entries, _ = parse_catalog(DEFAULT_README)
    results = search_entries(entries, category="PaaS")
    assert len(results) > 10
    for r in results:
        assert "paas" in r["category"].lower()


def test_search_entries_no_card():
    entries, _ = parse_catalog(DEFAULT_README)
    results = search_entries(entries, no_card_only=True)
    assert len(results) > 0
    for r in results:
        assert is_no_card(r)


def test_parse_catalog_missing_file(tmp_path: Path):
    missing_file = tmp_path / "nonexistent.md"
    with pytest.raises(FileNotFoundError):
        parse_catalog(missing_file)
