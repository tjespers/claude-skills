#!/usr/bin/env python3
"""Render specs/roadmap.json to human-readable formats."""

import argparse
import json
import os
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

REQUIRED_ITEM_FIELDS = ("id", "title", "status", "who", "why", "goals", "non_goals")


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

    if "key" not in data or not isinstance(data["key"], str) or not data["key"].strip():
        print(
            'Error: roadmap.json must have a top-level "key" field (e.g., "SCHED"). '
            "This is the project prefix used in item IDs (e.g., SCHED-0001). "
            "Add it to your roadmap.json and re-run.",
            file=sys.stderr,
        )
        sys.exit(1)

    key = data["key"]
    expected_prefix = f"{key}-"

    for i, item in enumerate(data["items"]):
        for field in REQUIRED_ITEM_FIELDS:
            if field not in item:
                print(f"Error: item {i} missing required field: {field}", file=sys.stderr)
                sys.exit(1)

        item_id = item["id"]
        if not item_id.startswith(expected_prefix):
            print(
                f"Error: item {i} id '{item_id}' must start with '{expected_prefix}' "
                f"(e.g., {key}-0001)",
                file=sys.stderr,
            )
            sys.exit(1)
        seq_part = item_id[len(expected_prefix):]
        if not seq_part.isdigit() or len(seq_part) != 4:
            print(
                f"Error: item {i} id '{item_id}' must end with a 4-digit number "
                f"(e.g., {key}-0001)",
                file=sys.stderr,
            )
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

        if "dependencies" in item:
            if not isinstance(item["dependencies"], list):
                print(f"Error: item {i} 'dependencies' must be an array", file=sys.stderr)
                sys.exit(1)
            for dep in item["dependencies"]:
                if not isinstance(dep, str):
                    print(f"Error: item {i} dependency values must be strings", file=sys.stderr)
                    sys.exit(1)

        if "spec_folder" in item and not isinstance(item["spec_folder"], str):
            print(f"Error: item {i} 'spec_folder' must be a string path", file=sys.stderr)
            sys.exit(1)

    # Validate dependency references point to existing items.
    all_ids = {item["id"] for item in data["items"]}
    for i, item in enumerate(data["items"]):
        for dep in item.get("dependencies", []):
            if dep not in all_ids:
                print(
                    f"Error: item {i} ({item['id']}) depends on '{dep}' "
                    f"which does not exist in the roadmap",
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


def item_anchor(item: dict) -> str:
    """Generate heading anchor for an item (matches GitHub auto-generated anchors)."""
    return slugify(f"{item['id']}. {item['title']}")


def render_markdown(data: dict, project_root: Path, output_dir: Path) -> str:
    """Render roadmap data to Markdown.

    Args:
        data: Parsed roadmap.json contents.
        project_root: Project root directory (spec_folder paths are relative to this).
        output_dir: Directory where ROADMAP.md will be written (links are relative to this).
    """
    items = data["items"]
    id_to_item = {item["id"]: item for item in items}

    lines = [
        "<!-- Auto-generated from roadmap.json \u2014 do not edit directly -->",
        "",
        "# Roadmap",
        "",
        "> Project-level view of features: from idea through specification to delivery.",
        "> Items are ordered by priority (top = highest).",
        "",
    ]

    if items:
        # Summary table
        lines.append("| ID | Feature | Status | Spec draft |")
        lines.append("|-----|---------|--------|:---:|")
        for item in items:
            icon, label = STATUS_DISPLAY[item["status"]]
            anchor = item_anchor(item)
            draft = "\u2713" if item.get("primer") else ""
            lines.append(
                f"| {item['id']} | [{item['title']}](#{anchor}) "
                f"| {icon} {label} | {draft} |"
            )
        lines.append("")

        # Detail sections
        for item in items:
            icon, label = STATUS_DISPLAY[item["status"]]
            lines.append("---")
            lines.append("")
            lines.append(f"### {item['id']}. {item['title']}")
            lines.append(f"**Status:** {icon} {label}")
            lines.append("")

            # Artifact links
            if item.get("spec_folder"):
                folder = item["spec_folder"]
                artifact_files = ["quickstart.md", "spec.md", "plan.md"]
                links = []
                for artifact in artifact_files:
                    artifact_abs = (project_root / folder / artifact).resolve()
                    if artifact_abs.exists():
                        link_label = artifact.replace(".md", "")
                        link_path = os.path.relpath(artifact_abs, output_dir.resolve())
                        links.append(f"[{link_label}]({link_path})")
                if links:
                    lines.append(f"**Artifacts:** {' \u2014 '.join(links)}")
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

            # Dependencies
            if item.get("dependencies"):
                dep_links = []
                for dep_id in item["dependencies"]:
                    dep_item = id_to_item.get(dep_id)
                    if dep_item:
                        dep_anchor = item_anchor(dep_item)
                        dep_links.append(f"[{dep_id}](#{dep_anchor})")
                    else:
                        dep_links.append(dep_id)
                lines.append(f"**Depends on:** {', '.join(dep_links)}")
                lines.append("")

            # Primer / spec draft
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

    output_path = Path(args.output) if args.output else input_path.parent / "ROADMAP.md"

    if args.format == "md":
        content = render_markdown(
            data,
            project_root=Path.cwd(),
            output_dir=output_path.parent,
        )
    output_path.write_text(content)
    print(f"Rendered {len(data['items'])} items -> {output_path}")


if __name__ == "__main__":
    main()
