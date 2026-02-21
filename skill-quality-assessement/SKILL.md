---
name: skill-quality-assessment
description: Structured feedback collection and improvement tracking for skills. Provides two workflows - giving feedback on skill effectiveness after task execution, and processing feedback to implement improvements with audit trail.
metadata:
  version: 0.1.0
---

# Skill Quality Assessment

Systematic feedback collection and improvement tracking for skills. Supports two distinct workflows:

1. **Providing Feedback**: Document skill effectiveness issues and successes during task execution
2. **Processing Feedback**: Implement improvements and generate audit trail of changes

---

## Workflow 1: Providing Feedback

### When to Use This Workflow

Use this workflow when:
- Completing a task where you actively used another skill
- Encountering accuracy issues in skill documentation (wrong methods, broken examples)
- Discovering missing critical context that would have helped
- Identifying sections that are too verbose or redundant
- Finding especially effective content that should be preserved
- User requests skill review, performance review, or quality assessment

**Do NOT use** for:
- Tasks where no other skill was used
- General conversation without task execution
- Tasks where skill worked perfectly with nothing to report

### Output Location

By default, write feedback to: `.claude/skills/<skill-name>/FEEDBACK_<YYYYMMDD>.json` **unless instructed otherwise and only if the .claude folder already exists in the workspace**. If this default cannot be used, ask the user where to store the feedback.

**Naming convention**:
- `<skill-name>`: Name of skill being assessed (e.g., `constraint-programming`)
- `<YYYYMMDD>`: Date of assessment (e.g., `20260113`)

**Example**: `.claude/skills/constraint-programming/FEEDBACK_20260113.json`

If file exists (multiple tasks same day), append sequential number: `FEEDBACK_20260113_2.json`

### Output Format

Provide feedback as JSON conforming to [schema.json](schema.json). Focus on observable facts:

```json
{
  "skill": {
    "name": "constraint-programming",
    "date": "2024-01-12",
    "version": "1.0.0"
  },
  "agent": {
    "runtime": "VSCode",
    "models": ["claude-sonnet-4.5"]
  },
  "task": {
    "description": "Implement EnforceMaximumWeeklyHours constraint",
    "completion": "complete",
    "complexity": "moderate"
  },
  "autonomy": {
    "level": "mostly",
    "total_interventions": 2
  },
  "preserve": [
    {
      "item": "Quick start template in SKILL.md",
      "why": "Used as-is, saved setup time"
    }
  ],
  "feedback": [
    {
      "id": "f1",
      "area": "accuracy",
      "severity": "critical",
      "action": "replace",
      "file": "references/CORE_CLASSES.md",
      "summary": "Duration uses wrong method name",
      "description": "Skill references greaterThan() but Duration class has moreThan()",
      "rationale": "Code breaks immediately when used",
      "suggestions": [
        "Update all greaterThan() to moreThan()",
        "Add verification grep to catch similar issues"
      ],
      "required_intervention": true
    }
  ]
}
```

### Feedback Collection Process

#### 1. Complete Your Task First

Focus on the user's primary request. Gather feedback observations **during** execution but don't interrupt the task to write feedback.

#### 2. Log Issues As You Encounter Them

When something from the skill causes a problem or requires correction:
- Note the file/section where issue exists
- Document what broke or confused you
- Record what correction you made
- Mark if human intervention was required

#### 3. Note What Worked Well

Identify content that was:
- Used exactly as written (no modifications needed)
- Clear and immediately applicable
- Perfect level of detail

This signals what **not** to change.

#### 4. Provide Feedback After Task Completion

Generate the JSON feedback structure covering:
- **Preserve**: What worked exceptionally well
- **Feedback**: Issues encountered (critical to low severity)

See [GUIDELINES.md](references/GUIDELINES.md) for severity criteria, area definitions, and suggestion quality standards.

### Autonomy Assessment

Rate how independently you completed the task:

- **`fully`**: Completed without human intervention
- **`mostly`**: 1-2 minor corrections/clarifications needed
- **`semi`**: 3-5 interventions required
- **`low`**: 6+ interventions, constant guidance needed
- **`failed`**: Could not proceed, skill was ineffective

Count total interventions where human had to:
- Correct broken code from skill example
- Explain missing context
- Guide around wrong information
- Clarify ambiguous instructions

### Key Principles for Feedback

#### Be Specific

❌ "The examples section needs work"
✅ "Five examples in MULTI_SHIFT_PATTERNS.md (lines 60-120) repeat same weekly pattern with minor variations"

#### Focus on Impact

Every feedback item should explain:
- What the issue caused (test failed, confusion, wasted time)
- Why it matters (blocks progress, misleads, inefficient)

#### Suggest, Don't Prescribe

You report problems and desires. The skill architect decides implementation:

❌ "Change line 84 from X to Y"
✅ "Skill references greaterThan() but should use moreThan()"

#### Link to Interventions

If something required human correction, mark `required_intervention: true` and explain what intervention it caused.

### Common Feedback Areas

See [GUIDELINES.md](references/GUIDELINES.md) for complete area definitions. Quick reference:

**Accuracy issues** (critical):
- Wrong method/class names
- Non-existent references
- Broken code examples
- Outdated information

**Missing context** (critical):
- Essential domain knowledge not documented
- Known bugs/gotchas not mentioned
- Critical distinctions not explained

**Verbosity** (low/medium):
- Redundant examples
- Obvious explanations for target audience
- Duplicate information across files

**Structure** (medium):
- Hard to find information
- Poor file organization
- Missing navigation aids

### Tips for Quality Feedback

#### During Task Execution

Keep mental notes of:
- First moment you got stuck
- When you had to search external sources
- Examples you used verbatim
- Corrections you made to skill code

#### When Writing Feedback

- Prioritize issues that required intervention
- Group similar issues (e.g., all wrong method names)
- Be generous with "preserve" entries - signals matter
- Provide verification commands when suggesting fixes

#### Severity Guidelines

- **Critical**: Broken code, wrong information, blocks progress
- **High**: Missing essential context, causes significant confusion
- **Medium**: Inefficient, could be clearer, minor obstacles
- **Low**: Nice-to-have improvements, polish, optimization

See [GUIDELINES.md](references/GUIDELINES.md) for detailed severity criteria and examples.

---

## Workflow 2: Processing Feedback

### When to Use This Workflow

Use this workflow when:
- You are implementing improvements based on feedback
- You need to track changes for audit trail or changelog generation
- User requests documentation of what changed in response to feedback
- You need version history with change attribution

### Processing Overview

This workflow has **no prescribed process** - skill creators work however they prefer. The only requirement is creating an improvement output file documenting what changed.

**Freedom to choose:**
- Manual edits or automated tools
- All changes at once or incrementally
- Any file organization approach
- Custom verification steps

### Output Format

Create improvement audit trail as JSON conforming to [improvement-schema.json](improvement-schema.json):

```json
{
  "source": {
    "skill": {
      "name": "constraint-programming",
      "path": ".ai/skills/constraint-programming"
    },
    "feedback": "FEEDBACK_20260113.json",
    "version": "1.0.0"
  },
  "target": {
    "skill": {
      "name": "constraint-programming",
      "path": ".ai/skills/constraint-programming"
    },
    "version": "1.1.0"
  },
  "agent": {
    "runtime": "VSCode",
    "models": ["claude-sonnet-4.5"]
  },
  "changes": [
    {
      "feedback_id": "f1",
      "files": ["references/CORE_CLASSES.md"],
      "action": "added",
      "description": "Added DateTime API documentation with Timestamp, Duration, Date, Window classes including creation methods and comparison operators"
    }
  ]
}
```

### Output Location

By default, write to same directory as feedback file: `<skill-dir>/IMPROVEMENT_<YYYYMMDD>.json`

**Example**: `.ai/skills/constraint-programming/IMPROVEMENT_20260113.json`

For skill renames/moves, store in **target** skill directory.

### Change Documentation Structure

Each change entry requires:

- **`feedback_id`**: Links to feedback item (e.g., `"f1"`)
- **`files`**: Array of files modified (relative to skill path)
- **`action`**: Past-tense action taken (added, removed, fixed, replaced, clarified, condensed, expanded, restructured, reworded, moved, merged, split)
- **`description`**: What was changed (focus on WHAT, not WHY - reference feedback for rationale)

**Atomic actions**: One change entry per action type. If you both "added" documentation AND "updated" another section in same file, that's two separate entries.

**Multiple files**: If one action affects multiple files (e.g., moving content), list all files in the `files` array.

### Skill Evolution Support

The schema supports skill renames, moves, and splits:

**Standard update** (same name/path):
```json
{
  "source": {
    "skill": { "name": "constraint-programming", "path": ".ai/skills/constraint-programming" }
  },
  "target": {
    "skill": { "name": "constraint-programming", "path": ".ai/skills/constraint-programming" }
  }
}
```

**Skill rename/move**:
```json
{
  "source": {
    "skill": { "name": "old-name", "path": ".ai/skills/old-path" }
  },
  "target": {
    "skill": { "name": "new-name", "path": ".ai/skills/new-path" }
  }
}
```

**Skill split** (create multiple improvement files, one per target skill).

### After Processing

1. **Bump skill version** in SKILL.md frontmatter to match `target.version`
2. **Commit changes** with clear commit message referencing feedback
3. **(Optional)** Generate human-readable report with render_improvement.py

---

## Scripts & Tools

### render_feedback.py

Converts FEEDBACK_*.json to human-readable markdown report.

**Usage**:
```bash
python scripts/render_feedback.py path/to/FEEDBACK_20260113.json
```

**Output**: Generates `FEEDBACK_20260113.md` in same directory with:
- Summary table (skill, version, date, task, autonomy)
- Agent context (runtime, models)
- Table of Contents
- Feedback items grouped by severity
- Preserve items section
- Version footer

**When to use**: After creating feedback JSON, run script to generate markdown for easier human review.

### render_improvement.py

Converts IMPROVEMENT_*.json to human-readable markdown summary.

**Usage**:
```bash
python scripts/render_improvement.py path/to/IMPROVEMENT_20260113.json
```

**Output**: Generates `IMPROVEMENT_20260113.md` in same directory with:
- Skill transformation summary (source → target)
- Agent context
- Table of Contents
- Change summary table (feedback_id, files, action, description)
- Version footer

**When to use**: After creating improvement JSON, run script to generate markdown for documentation or changelog preparation.

---

## Reference Documentation

- **[GUIDELINES.md](references/GUIDELINES.md)**: Detailed severity criteria, area definitions, action guidelines, examples
- **[schema.json](schema.json)**: JSON Schema for feedback input validation
- **[improvement-schema.json](improvement-schema.json)**: JSON Schema for improvement output validation
