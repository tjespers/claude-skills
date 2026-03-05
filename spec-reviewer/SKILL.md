---
name: spec-reviewer
description: "Automated review of speckit specification and planning documents on GitHub PRs. Reads PR diff, identifies spec.md/plan.md files, analyzes for structural issues, internal inconsistencies, cross-reference errors, and requirement quality problems, then posts a GitHub review with inline comments. Use when: (1) user says 'review spec', 'review this spec PR', 'spec review', (2) user provides a PR number containing spec or plan documents, (3) user wants automated quality checks on speckit output before manual review, (4) user says 'review #NNN' and the PR contains specs/ files."
license: Apache-2.0
metadata:
  author: Tim Jespers <git@tjespers.dev>
  version: 1.0.0
---

# Spec Reviewer

Automated review of speckit specification and planning documents on GitHub PRs. Post structured review comments that flag inconsistencies, missing elements, and quality issues — so the author can focus on content and flow rather than reading every line.

## Context Resolution

Resolve PR context:

```bash
OWNER_REPO=$(gh repo view --json owner,name --jq '"\(.owner.login)/\(.name)"')
# PR number from argument or current branch
gh pr view {pr} --json number,title,headRefName,author --jq '{number, title, headRefName, author: .author.login}'
```

## Authentication

Same auth infrastructure as PR Shepherd. Check and use for all write operations:

```bash
bash scripts/gh-app-auth.sh --check
```

Write operations (posting reviews) use the auth wrapper. Read operations use default `gh` auth. See PR Shepherd's [github-app-setup.md](../pr-shepherd/references/github-app-setup.md) for first-time setup.

## Tone Calibration

Determine authorship before writing the review:

```bash
# Get commit authors on the PR
gh pr view {pr} --json commits --jq '.commits[].authors[].login'
# Get PR author
gh pr view {pr} --json author --jq '.author.login'
```

**If all commits are by bots/AI** (login contains `[bot]`, `claude`, `copilot`, or similar):
- Direct, no-fluff tone. No compliments, no softening language.
- State the issue. State why it matters. Move on.
- Example: "FR-003 and FR-007 both specify the same constraint on ordering. Remove the duplicate."

**If any commits are by a human author**:
- Still direct and efficient. No fluff, but not terse to the point of being curt.
- Brief acknowledgment of good patterns only when genuinely notable.
- Example: "FR-003 and FR-007 overlap — they both constrain ordering. Consider consolidating."

**Never**: sycophantic openers ("Great spec!"), unnecessary hedging ("You might want to consider perhaps..."), padding ("I noticed that...").

## Workflow

### 1. Gather PR Data

```bash
# Get changed files
gh api repos/{owner}/{repo}/pulls/{pr}/files --jq '.[] | {filename, status, additions, deletions}'

# Get full diff
gh pr diff {pr}
```

Identify document types in the diff:
- `specs/*/spec.md` → spec review (load [references/spec-checklist.md](references/spec-checklist.md))
- `specs/*/plan.md` → plan review (load [references/plan-checklist.md](references/plan-checklist.md))
- `specs/*/tasks.md` → task review (check alignment with plan)
- `specs/*/checklists/*.md` → checklist review (verify claims match spec)

If the user provided extra context (e.g., "pay attention to the dependency on SCHEDULING-15"), note it for use during analysis.

### 2. Read and Analyze

Read each document fully. For each review checklist dimension, check the document and collect **findings** — only issues, not passing checks. Categorize each finding:

| Severity | Meaning | Use for |
|----------|---------|---------|
| **blocker** | Breaks spec quality or creates downstream problems | Missing mandatory sections, contradictory requirements, untestable FRs |
| **issue** | Should be fixed but doesn't block | Numbering gaps, missing edge cases, vague success criteria |
| **nit** | Minor improvement, take it or leave it | Style inconsistencies, wording suggestions, optional enhancements |

For **cross-document analysis** (when both spec.md and plan.md are in the PR):
- Verify plan implements all spec FRs
- Check plan design decisions don't contradict spec requirements
- Confirm key entities from spec appear in plan's project structure

### 3. Submit Review

Post a GitHub review with inline comments on specific lines. Use `jq` to build the review payload:

```bash
COMMIT_SHA=$(gh api repos/{owner}/{repo}/pulls/{pr} --jq '.head.sha')

# Build review body + inline comments
jq -n \
  --arg commit_id "$COMMIT_SHA" \
  --arg body "$REVIEW_BODY" \
  --arg event "COMMENT" \
  --argjson comments "$COMMENTS_JSON" \
  '{commit_id: $commit_id, body: $body, event: $event, comments: $comments}' | \
  bash scripts/gh-app-auth.sh gh api repos/{owner}/{repo}/pulls/{pr}/reviews --input -
```

### Review Body Format

```markdown
## Spec Review — {Feature Name}

{1-2 sentence summary of overall quality + finding count by severity}

| Severity | Count |
|----------|-------|
| Blocker | {n} |
| Issue | {n} |
| Nit | {n} |

{If user provided extra context, note how it was applied}

🔍 _Reviewed using [Spec Reviewer](https://github.com/tjespers/claude-skills/tree/main/spec-reviewer)_
```

### Inline Comment Format

Each inline comment:
- Starts with severity tag: `**[blocker]**`, `**[issue]**`, or `**[nit]**`
- States the problem in one sentence
- States why it matters or what to do about it (one sentence)
- For blockers: suggests a concrete fix

Example:
```
**[issue]** FR-012 requires "visual distinction" for LOW-confidence items but no acceptance scenario tests this. Add an acceptance scenario under US2 that verifies the visual difference.
```

### 4. Present Summary

After posting, show the user:
- Total findings by severity
- Link to the review
- Any items that need human judgment (e.g., "FR-005 might be intentionally vague — flagged for your call")

## User-Provided Context

When the user provides extra context (architecture concerns, related tickets, specific focus areas):
- Apply it as an additional review lens
- Note in the review body what context was applied
- Flag findings that specifically relate to the provided context

Example: User says "review with SCHEDULING-20 in mind" → look for Filament-direct-to-Eloquent patterns, note where Application layer routing is missing.

## Anti-Patterns

- **Don't review non-spec files** — if the PR has both spec and code, only review spec/plan files
- **Don't rewrite the spec** — flag issues, don't provide full replacement text (except for blockers where a concrete fix helps)
- **Don't review passing checks** — no "FR numbering looks good!" comments
- **Don't submit empty reviews** — if no findings, say so in a brief PR comment instead of a formal review
- **Don't use APPROVE/REQUEST_CHANGES** — always use COMMENT event; this is advisory, not gatekeeping
