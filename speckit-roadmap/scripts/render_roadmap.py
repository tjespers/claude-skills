#!/usr/bin/env python3
"""Render specs/roadmap.json to human-readable formats."""

import argparse
import json
import re
import sys
from pathlib import Path

VALID_STATUSES = ("idea", "specified", "planned", "done")

STATUS_DISPLAY = {
    "idea": ("\U0001f4a1", "Idea"),
    "specified": ("\U0001f4cb", "Specified"),
    "planned": ("\U0001f4d0", "Planned"),
    "done": ("\u2705", "Done"),
}

REQUIRED_FIELDS = ("title", "status", "who", "why", "goals", "non_goals")


def load_roadmap(path: Path) -> dict:
    """Load and validate roadmap.json."""
    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError as e:
        print(f"Error: invalid JSON in {path}: {e}", file=sys.stderr)
        sys.exit(1)

    if not isinstance(data, dict) or "items" not in data:
        print('Error: roadmap.json must be an object with an "items" array', file=sys.stderr)
        sys.exit(1)

    for i, item in enumerate(data["items"]):
        for field in REQUIRED_FIELDS:
            if field not in item:
                print(f"Error: item {i} missing required field: {field}", file=sys.stderr)
                sys.exit(1)
        if item["status"] not in VALID_STATUSES:
            print(
                f"Error: item {i} has invalid status '{item['status']}'. "
                f"Valid: {', '.join(VALID_STATUSES)}",
                file=sys.stderr,
            )
            sys.exit(1)
        for list_field in ("goals", "non_goals"):
            if not isinstance(item[list_field], list):
                print(
                    f"Error: item {i} field '{list_field}' must be an array",
                    file=sys.stderr,
                )
                sys.exit(1)

    return data


def slugify(text: str) -> str:
    """Generate a GitHub-compatible heading anchor."""
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"\s+", "-", text.strip())
    return text


def render_markdown(data: dict) -> str:
    """Render roadmap data to Markdown."""
    items = data["items"]
    lines = [
        "<!-- Auto-generated from roadmap.json — do not edit directly -->",
        "",
        "# Roadmap",
        "",
        "> Project-level view of features: from idea through specification to delivery.",
        "> Items are ordered by priority (top = highest).",
        "",
    ]

    if items:
        lines.append("| # | Feature | Status | Spec draft |")
        lines.append("|---|---------|--------|:---:|")
        for i, item in enumerate(items, 1):
            icon, label = STATUS_DISPLAY[item["status"]]
            anchor = slugify(f"{i}. {item['title']}")
            draft = "\u2713" if item.get("primer") else ""
            lines.append(f"| {i} | [{item['title']}](#{anchor}) | {icon} {label} | {draft} |")
        lines.append("")

        for i, item in enumerate(items, 1):
            icon, label = STATUS_DISPLAY[item["status"]]
            lines.append("---")
            lines.append("")
            lines.append(f"### {i}. {item['title']}")
            lines.append(f"**Status:** {icon} {label}")
            lines.append("")
            lines.append(f"**Who:** {item['who']}")
            lines.append("")
            lines.append(f"**Why:** {item['why']}")
            lines.append("")
            lines.append("**Goals:**")
            for goal in item["goals"]:
                lines.append(f"- {goal}")
            lines.append("")
            lines.append("**Non-goals:**")
            for non_goal in item["non_goals"]:
                lines.append(f"- {non_goal}")
            lines.append("")
            if item.get("primer"):
                lines.append("<details>")
                lines.append("<summary><strong>Spec draft</strong></summary>")
                lines.append("")
                lines.append(item["primer"])
                lines.append("")
                lines.append("</details>")
                lines.append("")

        lines.append("---")

    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description="Render roadmap.json to Markdown")
    parser.add_argument("input", help="Path to roadmap.json")
    parser.add_argument(
        "-o", "--output",
        help="Output file path (default: ROADMAP.md in same directory as input)",
    )
    parser.add_argument(
        "-f", "--format",
        choices=["md"],
        default="md",
        help="Output format (default: md)",
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: {input_path} not found", file=sys.stderr)
        sys.exit(1)

    data = load_roadmap(input_path)

    if args.format == "md":
        content = render_markdown(data)
        default_name = "ROADMAP.md"

    output_path = Path(args.output) if args.output else input_path.parent / default_name
    output_path.write_text(content)
    print(f"Rendered {len(data['items'])} items -> {output_path}")


if __name__ == "__main__":
    main()
