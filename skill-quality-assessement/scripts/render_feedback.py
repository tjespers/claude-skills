#!/usr/bin/env python3
"""
Convert skill quality assessment JSON feedback to human-readable Markdown report.

Usage:
    python render_feedback.py <input.json> [output.md]

If output is not specified, uses same name as input with .md extension.
"""

import json
import sys
from pathlib import Path
from collections import Counter
from datetime import datetime


def load_feedback(json_path: Path) -> dict:
    """Load and parse JSON feedback file."""
    with open(json_path, 'r') as f:
        return json.load(f)


def count_by_severity(feedback_items: list) -> dict:
    """Count feedback items by severity."""
    return Counter(item['severity'] for item in feedback_items)


def count_by_area(feedback_items: list) -> dict:
    """Count feedback items by area."""
    return Counter(item['area'] for item in feedback_items)


def group_by_severity(feedback_items: list) -> dict:
    """Group feedback items by severity level."""
    groups = {'critical': [], 'high': [], 'medium': [], 'low': []}
    for item in feedback_items:
        severity = item['severity']
        if severity in groups:
            groups[severity].append(item)
    return groups


def group_by_file(feedback_items: list) -> dict:
    """Group feedback items by file."""
    groups = {}
    for item in feedback_items:
        file = item.get('file', 'N/A')
        if file not in groups:
            groups[file] = []
        groups[file].append(item['id'])
    return groups


def render_toc(data: dict) -> str:
    """Generate table of contents based on sections."""
    lines = []
    lines.append("## Table of Contents")
    lines.append("")
    lines.append("1. [Summary](#-summary)")
    lines.append("2. [What to Preserve](#-what-to-preserve)")
    
    # Add severity sections if they have items
    grouped = group_by_severity(data['feedback'])
    section_number = 3
    
    severity_sections = [
        ('critical', 'Critical Issues (Requires Immediate Attention)'),
        ('high', 'High Priority Issues'),
        ('medium', 'Medium Priority Improvements'),
        ('low', 'Low Priority Enhancements')
    ]
    
    for severity_key, section_title in severity_sections:
        if grouped.get(severity_key):
            lines.append(f"{section_number}. [{section_title}](#{severity_key.replace(' ', '-').lower()}-issues)")
            section_number += 1
    
    lines.append(f"{section_number}. [Action Checklist](#-action-checklist)")
    section_number += 1
    lines.append(f"{section_number}. [Files Requiring Changes](#-files-requiring-changes)")
    lines.append("")
    
    return '\n'.join(lines)


def render_summary_table(feedback_items: list) -> str:
    """Render summary statistics table."""
    counts_by_area = count_by_area(feedback_items)

    # Get unique areas and severities
    areas = sorted(set(item['area'] for item in feedback_items))
    severities = ['critical', 'high', 'medium', 'low']

    # Count by area and severity
    area_severity_counts = {}
    for area in areas:
        area_severity_counts[area] = {}
        for severity in severities:
            count = sum(1 for item in feedback_items
                       if item['area'] == area and item['severity'] == severity)
            area_severity_counts[area][severity] = count

    # Build table
    lines = []
    lines.append("| Category | Critical | High | Medium | Low | Total |")
    lines.append("|----------|----------|------|--------|-----|-------|")

    totals = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0, 'total': 0}

    for area in areas:
        counts = area_severity_counts[area]
        total = sum(counts.values())
        area_display = area.replace('_', ' ').title()
        lines.append(f"| {area_display} | {counts['critical']} | {counts['high']} | {counts['medium']} | {counts['low']} | {total} |")

        for severity in severities:
            totals[severity] += counts[severity]
        totals['total'] += total

    lines.append(f"| **Total** | **{totals['critical']}** | **{totals['high']}** | **{totals['medium']}** | **{totals['low']}** | **{totals['total']}** |")

    return '\n'.join(lines)


def render_preserve_section(preserve_items: list) -> str:
    """Render the preserve section."""
    if not preserve_items:
        return "_No items marked for preservation_"

    lines = []
    for item in preserve_items:
        lines.append(f"- ✅ **{item['item']}**  ")
        lines.append(f"  _{item['why']}_")
        lines.append("")

    return '\n'.join(lines)


def render_feedback_item(item: dict) -> str:
    """Render a single feedback item with metadata table."""
    lines = []

    # Title
    lines.append(f"### [{item['id']}] {item['summary']}")
    lines.append("")

    # Metadata table
    intervention = "✅ Yes" if item.get('required_intervention', False) else "❌ No"
    file_display = f"`{item.get('file', 'N/A')}`"

    lines.append("| ID | Area | Severity | Action | Intervention | File |")
    lines.append("|----|------|----------|--------|--------------|------|")
    lines.append(f"| {item['id']} | {item['area'].replace('_', ' ')} | {item['severity']} | {item['action']} | {intervention} | {file_display} |")
    lines.append("")

    # Description
    lines.append("**Problem**:  ")
    lines.append(item['description'])
    lines.append("")

    # Rationale
    lines.append("**Impact**:  ")
    lines.append(item['rationale'])
    lines.append("")

    # Suggestions
    if item.get('suggestions'):
        lines.append("**Suggestions**:")
        for i, suggestion in enumerate(item['suggestions'], 1):
            lines.append(f"{i}. {suggestion}")
        lines.append("")

    lines.append("---")
    lines.append("")

    return '\n'.join(lines)


def render_action_checklist(feedback_items: list) -> str:
    """Render action checklist sorted by severity."""
    lines = []

    severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
    sorted_items = sorted(feedback_items, key=lambda x: severity_order[x['severity']])

    for item in sorted_items:
        severity_label = item['severity'].capitalize()
        lines.append(f"- [ ] **{item['id']}** - {item['summary']} ({severity_label})")

    return '\n'.join(lines)


def render_files_section(feedback_items: list) -> str:
    """Render files requiring changes section."""
    file_groups = group_by_file(feedback_items)

    lines = []
    for file, item_ids in sorted(file_groups.items()):
        count = len(item_ids)
        ids_str = ', '.join(item_ids)
        lines.append(f"- `{file}` ({count} issue{'s' if count > 1 else ''}: {ids_str})")

    return '\n'.join(lines)


def count_interventions_preventable(feedback_items: list) -> int:
    """Count how many items required intervention."""
    return sum(1 for item in feedback_items if item.get('required_intervention', False))


def render_markdown(data: dict) -> str:
    """Render complete markdown report."""
    lines = []

    # Header
    skill_name = data['skill']['name']
    skill_version = data['skill'].get('version', 'N/A')
    skill_date = data['skill'].get('date', 'N/A')

    # Agent info
    agent = data.get('agent', {})
    runtime = agent.get('runtime', 'N/A')
    models = agent.get('models', [])
    models_display = ', '.join(models) if models else 'N/A'

    # Task info
    task = data.get('task', {})
    task_description = task.get('description', 'N/A')
    task_complexity = task.get('complexity', 'N/A')
    task_completion = task.get('completion', 'N/A')

    # Autonomy info
    autonomy = data.get('autonomy', {})
    autonomy_level = autonomy.get('level', 'N/A')
    total_interventions = autonomy.get('total_interventions', 0)

    lines.append(f"# Skill Assessment: {skill_name}")
    lines.append("")
    
    # Context table
    lines.append("| Aspect | Value |")
    lines.append("|--------|-------|")
    lines.append(f"| **Skill** | {skill_name} |")
    lines.append(f"| **Version** | {skill_version} |")
    lines.append(f"| **Date** | {skill_date} |")
    lines.append(f"| **Task** | {task_description} |")
    lines.append(f"| **Complexity** | {task_complexity} |")
    lines.append(f"| **Completion** | {task_completion} |")
    lines.append(f"| **Autonomy** | {autonomy_level} ({total_interventions} intervention{'s' if total_interventions != 1 else ''}) |")
    lines.append(f"| **Runtime** | {runtime} |")
    lines.append(f"| **Model(s)** | {models_display} |")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # Table of Contents
    lines.append(render_toc(data))
    lines.append("---")
    lines.append("")

    # Summary
    lines.append("## 📊 Summary")
    lines.append("")
    lines.append(render_summary_table(data['feedback']))
    lines.append("")
    lines.append(f"**Items to Preserve**: {len(data.get('preserve', []))}")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Preserve section
    lines.append("## 🎯 What to Preserve")
    lines.append("")
    lines.append("> Content that worked exceptionally well - **do not change heavily**")
    lines.append("")
    lines.append(render_preserve_section(data.get('preserve', [])))
    lines.append("")
    lines.append("---")
    lines.append("")

    # Feedback sections by severity
    grouped = group_by_severity(data['feedback'])

    severity_config = [
        ('critical', '🚨 Critical Issues (Requires Immediate Attention)', 'critical'),
        ('high', '⚠️ High Priority Issues', 'high'),
        ('medium', '📝 Medium Priority Improvements', 'medium'),
        ('low', '💡 Low Priority Enhancements', 'low')
    ]

    for severity_key, section_title, _ in severity_config:
        items = grouped.get(severity_key, [])
        if not items:
            continue

        lines.append(f"## {section_title}")
        lines.append("")

        for item in items:
            lines.append(render_feedback_item(item))

        lines.append("")

    # Action checklist
    lines.append("## 📋 Action Checklist")
    lines.append("")
    lines.append(render_action_checklist(data['feedback']))
    lines.append("")

    preventable = count_interventions_preventable(data['feedback'])
    total_interventions = data['autonomy']['total_interventions']
    current_level = data['autonomy']['level']

    if preventable > 0:
        lines.append("")
        lines.append(f"**Estimated Impact**: Would eliminate **{preventable}/{total_interventions}** intervention{'s' if total_interventions != 1 else ''}")

    lines.append("")
    lines.append("---")
    lines.append("")

    # Files section
    lines.append("## 📂 Files Requiring Changes")
    lines.append("")
    lines.append(render_files_section(data['feedback']))
    lines.append("")
    lines.append("---")
    lines.append("")

    # Version footer
    lines.append(f"_skill-quality-assessment v0.1.0 | Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_")

    return '\n'.join(lines)


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python render_feedback.py <input.json> [output.md]")
        sys.exit(1)

    input_path = Path(sys.argv[1])

    if not input_path.exists():
        print(f"Error: Input file '{input_path}' not found")
        sys.exit(1)

    # Determine output path
    if len(sys.argv) >= 3:
        output_path = Path(sys.argv[2])
    else:
        output_path = input_path.with_suffix('.md')

    # Load and render
    try:
        data = load_feedback(input_path)
        markdown = render_markdown(data)

        # Write output
        with open(output_path, 'w') as f:
            f.write(markdown)

        print(f"✅ Report generated: {output_path}")

    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {input_path}: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
