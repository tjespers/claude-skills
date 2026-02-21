#!/usr/bin/env python3
"""
Convert skill improvement JSON to human-readable Markdown summary.

Usage:
    python render_improvement.py <input.json> [output.md]

If output is not specified, uses same name as input with .md extension.
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from collections import Counter


def load_improvement(json_path: Path) -> dict:
    """Load and parse JSON improvement file."""
    with open(json_path, 'r') as f:
        return json.load(f)


def count_by_action(changes: list) -> dict:
    """Count changes by action type."""
    return Counter(change['action'] for change in changes)


def group_by_feedback_id(changes: list) -> dict:
    """Group changes by feedback ID."""
    groups = {}
    for change in changes:
        fid = change['feedback_id']
        if fid not in groups:
            groups[fid] = []
        groups[fid].append(change)
    return groups


def get_unique_files(changes: list) -> set:
    """Get unique set of files modified."""
    files = set()
    for change in changes:
        for file in change['files']:
            files.add(file)
    return files


def render_toc(data: dict) -> str:
    """Generate table of contents."""
    lines = []
    lines.append("## Table of Contents")
    lines.append("")
    lines.append("1. [Transformation Summary](#transformation-summary)")
    lines.append("2. [Change Overview](#change-overview)")
    lines.append("3. [Changes by Feedback Item](#changes-by-feedback-item)")
    lines.append("4. [Files Modified](#files-modified)")
    lines.append("")
    return '\n'.join(lines)


def render_transformation_summary(data: dict) -> str:
    """Render source → target transformation summary."""
    source = data['source']
    target = data['target']
    
    lines = []
    lines.append("## Transformation Summary")
    lines.append("")
    lines.append("| Aspect | Before (Source) | After (Target) |")
    lines.append("|--------|-----------------|----------------|")
    lines.append(f"| **Skill Name** | {source['skill']['name']} | {target['skill']['name']} |")
    lines.append(f"| **Skill Path** | `{source['skill']['path']}` | `{target['skill']['path']}` |")
    lines.append(f"| **Version** | {source['version']} | {target['version']} |")
    lines.append(f"| **Feedback Source** | {source['feedback']} | — |")
    lines.append("")
    
    # Agent info
    agent = data.get('agent', {})
    runtime = agent.get('runtime', 'N/A')
    models = agent.get('models', [])
    models_display = ', '.join(models) if models else 'N/A'
    
    lines.append(f"**Processed by**: {runtime} using {models_display}")
    lines.append("")
    
    return '\n'.join(lines)


def render_change_overview(data: dict) -> str:
    """Render high-level change statistics."""
    changes = data['changes']
    
    lines = []
    lines.append("## Change Overview")
    lines.append("")
    
    # Count by action
    action_counts = count_by_action(changes)
    
    lines.append("| Metric | Count |")
    lines.append("|--------|-------|")
    lines.append(f"| **Total Changes** | {len(changes)} |")
    lines.append(f"| **Files Modified** | {len(get_unique_files(changes))} |")
    lines.append(f"| **Feedback Items Addressed** | {len(group_by_feedback_id(changes))} |")
    lines.append("")
    
    lines.append("**Changes by Action Type**:")
    lines.append("")
    for action, count in sorted(action_counts.items()):
        lines.append(f"- **{action}**: {count}")
    lines.append("")
    
    return '\n'.join(lines)


def render_changes_by_feedback(data: dict) -> str:
    """Render changes grouped by feedback ID."""
    changes = data['changes']
    grouped = group_by_feedback_id(changes)
    
    lines = []
    lines.append("## Changes by Feedback Item")
    lines.append("")
    
    for fid in sorted(grouped.keys()):
        changes_for_fid = grouped[fid]
        lines.append(f"### {fid}")
        lines.append("")
        
        for change in changes_for_fid:
            files_display = ', '.join(f"`{f}`" for f in change['files'])
            lines.append(f"**Action**: {change['action']}  ")
            lines.append(f"**Files**: {files_display}  ")
            lines.append(f"**Description**: {change['description']}")
            lines.append("")
        
        lines.append("---")
        lines.append("")
    
    return '\n'.join(lines)


def render_files_modified(data: dict) -> str:
    """Render table of files modified with change counts."""
    changes = data['changes']
    
    # Count changes per file
    file_changes = {}
    file_actions = {}
    
    for change in changes:
        action = change['action']
        for file in change['files']:
            if file not in file_changes:
                file_changes[file] = 0
                file_actions[file] = set()
            file_changes[file] += 1
            file_actions[file].add(action)
    
    lines = []
    lines.append("## Files Modified")
    lines.append("")
    lines.append("| File | Changes | Actions |")
    lines.append("|------|---------|---------|")
    
    for file in sorted(file_changes.keys()):
        count = file_changes[file]
        actions = ', '.join(sorted(file_actions[file]))
        lines.append(f"| `{file}` | {count} | {actions} |")
    
    lines.append("")
    
    return '\n'.join(lines)


def render_markdown(data: dict) -> str:
    """Render complete markdown report."""
    lines = []
    
    # Header
    source_skill = data['source']['skill']['name']
    source_version = data['source']['version']
    target_version = data['target']['version']
    
    lines.append(f"# Skill Improvement: {source_skill}")
    lines.append("")
    lines.append(f"**Version Transition**: {source_version} → {target_version}")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # Table of Contents
    lines.append(render_toc(data))
    lines.append("---")
    lines.append("")
    
    # Transformation summary
    lines.append(render_transformation_summary(data))
    lines.append("---")
    lines.append("")
    
    # Change overview
    lines.append(render_change_overview(data))
    lines.append("---")
    lines.append("")
    
    # Changes by feedback
    lines.append(render_changes_by_feedback(data))
    lines.append("---")
    lines.append("")
    
    # Files modified
    lines.append(render_files_modified(data))
    lines.append("---")
    lines.append("")
    
    # Version footer
    lines.append(f"_skill-quality-assessment v0.1.0 | Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_")
    
    return '\n'.join(lines)


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python render_improvement.py <input.json> [output.md]")
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
        data = load_improvement(input_path)
        markdown = render_markdown(data)
        
        # Write output
        with open(output_path, 'w') as f:
            f.write(markdown)
        
        print(f"✅ Improvement summary generated: {output_path}")
    
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {input_path}: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
