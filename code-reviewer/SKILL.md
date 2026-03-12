---
name: code-reviewer
description: >
  Automated code review for implementation PRs against their speckit specification.
  Verifies that code delivers what the spec promises — FR coverage, design decision compliance,
  architecture layer discipline, entity/DTO alignment, and phantom feature detection.
  Does NOT check test quality, SAST, or code style — those are handled by CI pipelines.
  Use when: (1) user says 'review code', 'code review', 'review implementation',
  (2) user provides an implementation PR number and wants spec-compliance verification,
  (3) user says 'review #NNN' and the PR contains source code (not spec files),
  (4) user wants to verify implementation matches the spec before merging.
license: Apache-2.0
metadata:
  author: Tim Jespers <tjespers@shiftbase.com>
  version: 1.0.0
---

# Code Reviewer

Verify that an implementation PR delivers what its spec promises. Complements CI pipelines (tests, SAST, linting) by checking the semantic gap: does the code actually implement the specified requirements?

## Context Resolution

```bash
OWNER_REPO=$(gh repo view --json owner,name --jq '"\(.owner.login)/\(.name)"')
gh pr view {pr} --json number,title,headRefName,author --jq '{number, title, headRefName, author: .author.login}'
```

## Spec Discovery

Derive the spec directory from the PR's branch name:

```bash
BRANCH=$(gh pr view {pr} --json headRefName --jq '.headRefName')
# Branch pattern: NNN-feature-name → specs/NNN-feature-name/
SPEC_DIR="specs/${BRANCH}"
```

If `specs/{branch}/` doesn't exist in the repo, check PR title for a spec number pattern (e.g., `SCHEDULING-N / spec-NNN:`), or ask the user.

Read the spec artifacts in order. Stop at each layer — not all specs have all artifacts:

1. `spec.md` — FRs, acceptance scenarios, key entities (required)
2. `plan.md` — design decisions, project structure, constitution check (required)
3. `data-model.md` — entity schemas, JSON structures, migration plan (if exists)
4. `tasks.md` — implementation task list with completion status (if exists)

Use `gh api` to read files from the **base branch** (not the PR branch), since spec artifacts are typically merged before implementation begins:

```bash
# Read spec from base branch
gh api repos/{owner}/{repo}/contents/{path} --jq '.content' -H "Accept: application/vnd.github.v3+json" | base64 -d
```

If the spec files are not on the base branch, check the PR branch itself — some workflows keep spec and implementation in the same PR.

## Authentication

Same auth infrastructure as PR Shepherd and Spec Reviewer:

```bash
bash scripts/gh-app-auth.sh --check
```

Write operations (posting reviews) use the auth wrapper. Read operations use default `gh` auth.

## Tone Calibration

Same rules as spec-reviewer — check commit authorship:

```bash
gh pr view {pr} --json commits --jq '.commits[].authors[].login'
```

**All bot/AI authors**: Direct, no-fluff. State the gap. State what's missing.
**Any human authors**: Direct but not terse. Brief context on why the gap matters.

## Workflow

### 1. Load Spec Artifacts

Read spec.md and plan.md from the repo (base branch or PR branch). Extract:

- **FR list**: All FR-NNN entries with their MUST/SHOULD/MAY level
- **Design decisions**: All D1, D2, ... entries
- **Project structure**: Expected files with (NEW)/(MODIFIED) annotations
- **Key entities**: Entity names, attributes, relationships
- **Deferred items**: Struck-through FRs, "v2" items, explicitly deferred scope
- **Constitution gates**: Required patterns (strict_types, layer discipline, etc.)

If `data-model.md` exists, also extract:
- **Entity schemas**: Column types, nullability, JSON structures
- **DTO definitions**: Field names, types

### 2. Load PR Diff

```bash
gh api repos/{owner}/{repo}/pulls/{pr}/files --jq '.[] | {filename, status, additions, deletions}'
gh pr diff {pr}
```

Separate files into categories:
- **Source code**: `src/`, `app/`, `database/` — primary review targets
- **Tests**: `tests/` — note presence but don't review quality (CI handles this)
- **Config**: `composer.json`, config files — check for expected dependencies
- **Spec files**: `specs/` — skip (use spec-reviewer for these)

### 3. Analyze Against Spec

Load [references/code-checklist.md](references/code-checklist.md) and evaluate each dimension.

#### FR Coverage Matrix

Build a matrix mapping each FR to its implementation:

```
FR-001 → src/Application/.../Handler.php (line 45) ✅
FR-002 → src/AI/.../Agent.php (line 12) ✅
FR-003 → ??? ❌ NOT FOUND
FR-007 → ~~deferred to v2~~ ⏭️ SKIP
```

For each FR:
- **MUST + implemented**: Pass (don't report)
- **MUST + missing**: Blocker
- **MUST + partial**: Issue (state what's missing)
- **SHOULD + missing**: Issue
- **Deferred + implemented**: Issue (phantom feature / scope creep)

#### Design Decision Compliance

For each D-number in plan.md, verify the code follows it. Common checks:
- D says "separate model" → verify separate class exists, not inlined
- D says "handler receives plain data" → verify handler constructor/method signature
- D says "no persistence in handler" → verify handler doesn't call `save()`/`create()`

#### Architecture Spot-Check

Don't exhaustively trace every import — focus on the patterns most likely to be violated:
- Filament actions calling agents directly (should go through Application handler)
- Domain models importing Infrastructure classes
- Application handlers importing Filament classes

### 4. Submit Review

Same API pattern as spec-reviewer:

```bash
COMMIT_SHA=$(gh api repos/{owner}/{repo}/pulls/{pr} --jq '.head.sha')

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
## Code Review — {Feature Name} (Spec Compliance)

{1-2 sentence summary: how well does the implementation match the spec?}

### FR Coverage: {X}/{Y} implemented

| FR | Status | Location |
|----|--------|----------|
| FR-001 | ✅ | `src/.../File.php:45` |
| FR-002 | ❌ Missing | — |
| FR-003 | ⏭️ Deferred | per spec |

### Findings

| Severity | Count |
|----------|-------|
| Blocker | {n} |
| Issue | {n} |
| Nit | {n} |

{If user provided extra context, note how it was applied}

🔍 _Reviewed using [Code Reviewer](https://github.com/tjespers/claude-skills/tree/main/code-reviewer)_
```

### Inline Comment Format

Same severity tags as spec-reviewer: `**[blocker]**`, `**[issue]**`, `**[nit]**`.

Each comment references the specific FR, design decision, or architecture rule being violated:

```
**[blocker]** FR-003 (DissectionAgent MUST decompose into four dimensions) — this handler only extracts three dimensions. The `trigger` field is not populated anywhere in the response mapping.
```

```
**[issue]** D4 (handler-level concurrency guard) — plan specifies a `dissecting` flag check in the handler, but the handler proceeds without checking. The UI button-disable alone doesn't prevent concurrent runs from multiple tabs.
```

### 5. Present Summary

After posting, show the user:
- FR coverage ratio (e.g., "15/18 FRs implemented")
- Findings by severity
- Link to the review
- Items needing human judgment

## Scope Boundaries

**In scope** (this skill):
- FR coverage verification
- Design decision compliance
- Architecture layer discipline
- Entity/DTO field alignment with data-model.md
- Phantom feature detection (code beyond spec scope)
- Constitution compliance (strict_types, commit scopes, layer rules)

**Out of scope** (handled by CI/pipelines):
- Test quality or coverage percentage
- PHPStan/Larastan analysis
- Code style / formatting
- SAST / security scanning
- Behat / Pest test execution

## User-Provided Context

When the user provides extra context:
- Apply as additional review lens (same as spec-reviewer)
- Note in review body what context was applied

## Anti-Patterns

- **Don't review test quality** — CI handles that. Only check tests exist where plan says they should.
- **Don't review spec files in the PR** — use spec-reviewer for that
- **Don't suggest code improvements unrelated to spec** — this is compliance review, not code quality review
- **Don't flag code style** — linters and formatters handle that
- **Don't use APPROVE/REQUEST_CHANGES** — use COMMENT event unless user explicitly asks for approval
