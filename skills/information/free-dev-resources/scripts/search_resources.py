#!/usr/bin/env python3
"""CLI utility to query and filter free developer resources from free-for.dev catalog.

Parses resource-repo/README.md to support fast searches by category, keyword,
no-credit-card requirement, and exact service lookup.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

# Default path relative to this script:
DEFAULT_README = Path(__file__).resolve().parent.parent / "resource-repo" / "README.md"


def parse_catalog(
    readme_path: Path,
) -> tuple[list[dict[str, Any]], dict[str, list[dict[str, Any]]]]:
    """Parse resource-repo/README.md into structured resource entries.

    Returns:
        (entries, category_map)
    """
    if not readme_path.is_file():
        raise FileNotFoundError(f"Catalog file not found at: {readme_path.resolve()}")

    content = readme_path.read_text(encoding="utf-8")
    lines = content.splitlines()

    entries: list[dict[str, Any]] = []
    category_map: dict[str, list[dict[str, Any]]] = {}

    current_category: str | None = None
    parent_entry: dict[str, Any] | None = None

    top_item_pattern = re.compile(
        r"^\s{2,4}\*\s*\[([^\]]+)\]\(([^)]+)\)\s*(?:-\s*(.*))?$"
    )
    sub_item_pattern = re.compile(
        r"^\s{4,8}\*\s*(?:\[([^\]]+)\]\(([^)]+)\))?\s*(?:-\s*)?(.*)$"
    )

    for line in lines:
        if line.startswith("## "):
            current_category = line[3:].strip()
            parent_entry = None
            if current_category not in category_map:
                category_map[current_category] = []
            continue

        if current_category is None:
            # Skip header / table of contents before first ## section
            continue

        # Check for top-level service item
        top_match = top_item_pattern.match(line)
        if top_match:
            name, url, desc = top_match.groups()
            entry: dict[str, Any] = {
                "category": current_category,
                "name": name.strip(),
                "url": url.strip(),
                "description": (desc or "").strip(),
                "sub_items": [],
            }
            parent_entry = entry
            entries.append(entry)
            category_map.setdefault(current_category, []).append(entry)
            continue

        # Check for nested sub-service / sub-offering item
        sub_match = sub_item_pattern.match(line)
        if sub_match and parent_entry is not None:
            sub_name, sub_url, sub_desc = sub_match.groups()
            text = (sub_desc or "").strip()
            if sub_name:
                text = (
                    f"[{sub_name}]({sub_url}): {text}"
                    if sub_url
                    else f"{sub_name}: {text}"
                )
            if text:
                parent_entry["sub_items"].append(text)

    return entries, category_map


def is_no_card(entry: dict[str, Any]) -> bool:
    """Check if the description or sub-items indicate no credit card is required."""
    text = (
        entry["name"]
        + " "
        + entry["description"]
        + " "
        + " ".join(entry.get("sub_items", []))
    ).lower()
    no_card_signals = [
        "no credit card",
        "no card required",
        "without credit card",
        "no card needed",
        "no payment details needed",
        "no card",
        "no credit-card",
    ]
    return any(signal in text for signal in no_card_signals)


def search_entries(
    entries: list[dict[str, Any]],
    query: str | None = None,
    category: str | None = None,
    no_card_only: bool = False,
) -> list[dict[str, Any]]:
    """Filter entries according to query, category, and credit card criteria."""
    results: list[dict[str, Any]] = []
    query_terms = [q.lower() for q in query.split()] if query else []
    cat_query = category.lower() if category else None

    for entry in entries:
        if cat_query and cat_query not in entry["category"].lower():
            continue

        if no_card_only and not is_no_card(entry):
            continue

        if query_terms:
            searchable = (
                entry["name"]
                + " "
                + entry["category"]
                + " "
                + entry["description"]
                + " "
                + " ".join(entry.get("sub_items", []))
            ).lower()
            if not all(term in searchable for term in query_terms):
                continue

        results.append(entry)

    return results


def format_entry_text(entry: dict[str, Any]) -> str:
    """Format an entry for human-readable terminal output."""
    lines = [
        f"• {entry['name']} [{entry['category']}]",
        f"  URL: {entry['url']}",
    ]
    if entry["description"]:
        lines.append(f"  Summary: {entry['description']}")
    if entry.get("sub_items"):
        lines.append("  Offerings:")
        for sub in entry["sub_items"][:8]:  # Limit output length if long
            lines.append(f"    - {sub}")
        if len(entry["sub_items"]) > 8:
            lines.append(f"    ... and {len(entry['sub_items']) - 8} more")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Search free-for.dev developer resources catalog."
    )
    parser.add_argument(
        "--file",
        type=Path,
        default=DEFAULT_README,
        help="Path to resource-repo README.md",
    )
    parser.add_argument("--json", action="store_true", help="Output results as JSON")

    subparsers = parser.add_subparsers(dest="command", required=True)

    # Search command
    search_parser = subparsers.add_parser(
        "search", help="Search resources by keyword and criteria."
    )
    search_parser.add_argument("query", nargs="*", help="Keywords to search for")
    search_parser.add_argument("--category", "-c", help="Filter by category name")
    search_parser.add_argument(
        "--no-card",
        action="store_true",
        help="Only match offerings explicitly stating no credit card is required",
    )
    search_parser.add_argument(
        "--limit", "-n", type=int, default=15, help="Maximum results to return"
    )

    # Categories command
    subparsers.add_parser("categories", help="List all available categories.")

    # Category command
    cat_parser = subparsers.add_parser(
        "category", help="List all resources within a category."
    )
    cat_parser.add_argument(
        "category_name", help="Name or partial name of the category"
    )
    cat_parser.add_argument(
        "--limit", "-n", type=int, default=30, help="Maximum results to return"
    )

    # Inspect command
    inspect_parser = subparsers.add_parser(
        "inspect", help="Inspect a specific service by name."
    )
    inspect_parser.add_argument("name", help="Service name")

    args = parser.parse_args()

    try:
        entries, category_map = parse_catalog(args.file)
    except FileNotFoundError as err:
        print(f"Error: {err}", file=sys.stderr)
        sys.exit(1)

    if args.command == "categories":
        data = [
            {"category": cat, "count": len(items)}
            for cat, items in category_map.items()
        ]
        if args.json:
            print(json.dumps(data, indent=2))
        else:
            print(f"Catalog Categories ({len(data)} total):\n")
            for item in data:
                print(f"  • {item['category']} ({item['count']} items)")
        return

    if args.command == "category":
        target = args.category_name.lower()
        matched_cats = [c for c in category_map if target in c.lower()]
        if not matched_cats:
            print(
                f"No categories matched '{args.category_name}'. Run 'categories' to see available ones.",
                file=sys.stderr,
            )
            sys.exit(1)

        matched_entries = []
        for c in matched_cats:
            matched_entries.extend(category_map[c])

        limit = args.limit
        results = matched_entries[:limit]

        if args.json:
            print(json.dumps(results, indent=2))
        else:
            print(
                f"Found {len(matched_entries)} entries in category matching '{args.category_name}' (showing top {len(results)}):\n"
            )
            for e in results:
                print(format_entry_text(e))
                print()
        return

    if args.command == "search":
        q = " ".join(args.query).strip() if args.query else None
        results = search_entries(
            entries=entries,
            query=q,
            category=args.category,
            no_card_only=args.no_card,
        )
        limited = results[: args.limit]

        if args.json:
            print(json.dumps(limited, indent=2))
        else:
            print(
                f"Found {len(results)} matching resources (showing {len(limited)}):\n"
            )
            for e in limited:
                print(format_entry_text(e))
                print()
        return

    if args.command == "inspect":
        target_name = args.name.lower()
        matched = [
            e
            for e in entries
            if target_name == e["name"].lower() or target_name in e["name"].lower()
        ]
        if not matched:
            print(f"No service found matching '{args.name}'.", file=sys.stderr)
            sys.exit(1)

        if args.json:
            print(json.dumps(matched, indent=2))
        else:
            for e in matched:
                print(format_entry_text(e))
                print()
        return


if __name__ == "__main__":
    main()
