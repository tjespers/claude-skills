---
name: speckit-roadmap
description: >
  Roadmap companion for spec-kit users. Decomposes big ideas into discrete,
  spec-worthy features and tracks them on a persistent roadmap (specs/roadmap.json).
  Use this skill when: (1) a brainstorming session reveals an idea that is really
  multiple specs, (2) a user wants to capture future feature ideas before they're
  ready for /speckit.specify, (3) a user wants to view, reorder, or update the
  status of items on their roadmap, (4) a user wants to pick the next item to
  spec out.
license: Apache-2.0
metadata:
  author: Tim Jespers <git@tjespers.dev>
  version: 2.0.0
---

# Speckit Roadmap

## Phase 0: Load Context

Silently load project context before engaging the user:

1. **Roadmap** — Read `specs/roadmap.json` if it exists. Note the project key, existing items (with their IDs), statuses, dependencies, and ordering. If the file exists but has no top-level `key` field or items lack `id` fields, this is a v1 roadmap that needs migration (see Migration section below).
2. **Constitution** — Read `.specify/memory/constitution.md` if it exists. Note principles and constraints that may affect decomposition or prioritization.
3. **Existing specs** — List `specs/` directories. Cross-reference with roadmap items using their `spec_folder` field (if set) to detect stale statuses (e.g., item has `spec_folder: "specs/001-coverage-tracking"` and that folder contains `spec.md`, but the item is still marked `idea`). For items without `spec_folder`, no automatic cross-referencing is possible.
4. **Codebase awareness** — Note language, framework, and structure from agent context files (CLAUDE.md, plan files) or quick inspection.

Do not report this to the user unless asked. Use it to ask smarter questions, catch conflicts, and flag stale statuses.

## Phase 1: Determine Mode

Determine which mode to operate in based on user input:

**User brings an idea or vision** → Brainstorm mode (Phase 2)
**User wants to work with the existing roadmap** → Management mode (Phase 4)

If the user's intent is ambiguous, ask which mode they'd like.

---

## Brainstorm Mode

### Phase 2: Decompose

Take the user's idea (provided as arguments or in conversation) and break it into discrete, independently specifiable features.

#### Step 1: Propose a breakdown

Analyze the idea and propose a decomposition as a numbered list with working titles and one-sentence summaries:

> **Proposed breakdown:**
> 1. **[Title]** — [one-sentence summary]
> 2. **[Title]** — [one-sentence summary]
> 3. **[Title]** — [one-sentence summary]

Then ask the user to confirm, merge, split, or add items before proceeding.

#### Step 2: Refine each item interactively

For each confirmed item, shape a rich description through conversation:

1. Present a draft covering the four schema fields:
   - **Who** — who benefits from this feature
   - **Why** — what problem it solves or opportunity it creates
   - **Goals** — concrete outcomes from the user's perspective (bulleted list)
   - **Non-goals** — what is explicitly out of scope (bulleted list)

   Present as:

   > **[ID] — [Title]:**
   > **Who:** [who]
   > **Why:** [why]
   > **Goals:**
   > - [goal 1]
   > - [goal 2]
   > **Non-goals:**
   > - [non-goal 1]

2. Ask the user if the draft captures their intent or needs adjustment.
3. Iterate until the user is satisfied, then move to the next item.

Keep it lighter than full specification — this is shaping for the roadmap, not a complete spec.

#### Steering away from implementation

If the user starts describing HOW something should be built, gently redirect:
- Acknowledge their technical thinking
- Reframe in terms of user needs: "So from the user's perspective, what you're describing is [behavior]. Let's capture that intent — the technical details come later during `/speckit.specify` and `/speckit.plan`."
- If implementation details reveal important constraints, capture those as scope notes rather than requirements

#### Catching conflicts

Use project context from Phase 0 to:
- Flag when a proposed item overlaps significantly with an existing roadmap item or spec
- Note when an item would conflict with a constitution principle
- Highlight when items in the breakdown overlap with each other (candidates for merging)

Raise these as observations, not blockers. The user decides how to proceed.

#### Step 3: Final confirmation

Once all items are refined, present the complete set:

> **Ready to add to roadmap:**
>
> **[ID]. [Title]**
> **Who:** ... | **Why:** ...
> **Goals:** ... | **Non-goals:** ...
>
> **[ID]. [Title]**
> **Who:** ... | **Why:** ...
> **Goals:** ... | **Non-goals:** ...

Ask the user to confirm before writing.

### Phase 3: Write and Render

After user confirmation, write the items to `specs/roadmap.json` and render.

#### JSON schema

`specs/roadmap.json` structure:

```json
{
  "key": "PROJ",
  "items": [
    {
      "id": "PROJ-0001",
      "title": "Short descriptive name",
      "status": "idea",
      "spec_folder": "specs/001-feature-name",
      "dependencies": ["PROJ-0003"],
      "who": "Who benefits from this feature.",
      "why": "What problem it solves or opportunity it creates.",
      "goals": ["Outcome 1", "Outcome 2"],
      "non_goals": ["Explicitly excluded 1", "Explicitly excluded 2"],
      "primer": "(optional) Natural language description ready for /speckit.specify"
    }
  ]
}
```

**Top-level fields:**
- `key` (required) — Project prefix for item IDs. Short uppercase string (e.g., "SCHED", "PROJ"). Set once when the roadmap is created.

**Per-item fields:**
- `id` (required) — Stable identifier in format `{key}-{4-digit sequence}` (e.g., "SCHED-0001"). Auto-assigned by the skill; never reused or changed. IDs are stable across reordering.
- `title` (required) — Short descriptive name.
- `status` (required) — One of: `idea`, `specified`, `planned`, `done`.
- `spec_folder` (optional) — Relative path to the spec artifacts directory (e.g., "specs/001-coverage-tracking"). Set when the item progresses past `idea` status. Used by the render script to generate artifact links.
- `dependencies` (optional) — Array of item IDs this item depends on (e.g., ["SCHED-0003"]). Used by the render script to generate cross-reference links.
- `who` (required) — Who benefits from this feature.
- `why` (required) — What problem it solves or opportunity it creates.
- `goals` (required) — Array of concrete outcomes.
- `non_goals` (required) — Array of explicitly excluded items.
- `primer` (optional) — Natural language description ready for /speckit.specify.

Array order = priority order (first = highest priority). Reordering does not affect IDs.

Status values map to the speckit workflow:
- `idea` — captured on the roadmap, not yet specified
- `specified` — `/speckit.specify` has been run, `spec.md` exists
- `planned` — `/speckit.plan` has been run, `plan.md` exists
- `done` — implemented and shipped

**ID assignment rules:**
When adding new items, find the highest existing sequence number across all items, increment by 1, and zero-pad to 4 digits. Example: if the highest existing ID is SCHED-0012, the next item gets SCHED-0013. IDs are never reused — if SCHED-0005 is removed, the next new item still gets the next number after the current highest.

#### Writing the roadmap

- **New roadmap**: Ask the user for a project key (short uppercase string, e.g., "SCHED"). Create `specs/roadmap.json` with the `key` field and the items array. Auto-assign IDs starting from `{key}-0001`.
- **Existing roadmap**: Read the current file, note the `key` and the highest existing sequence number. Append new items with auto-assigned IDs (incrementing from the highest). Write back.

#### Rendering

After every write, run the render script to produce a human-readable Markdown view:

```bash
scripts/render_roadmap.py specs/roadmap.json
```

This outputs `specs/ROADMAP.md` — a summary table with status indicators linking to detailed item descriptions below.

#### Handoff

After writing and rendering, offer to start specifying one of the items:

"These items are now on your roadmap. Want to start specifying one of them now?"

If the user picks an item, hand off to `/speckit.specify`. Use the item's `primer` field if it exists; otherwise compose a natural language description from the structured fields (who, why, goals, non-goals). If not, close the session — items are persisted and the user can return later.

---

## Management Mode

### Phase 4: Roadmap Operations

When the user wants to work with their existing roadmap, support these operations. After any modification, re-run the render script.

#### View
Display the current roadmap with statuses and IDs. If stale statuses were detected in Phase 0 (via `spec_folder` cross-referencing), surface them:

> "I noticed [ID] [Title] is still marked as `idea` but its spec folder (`[spec_folder]`) already contains `spec.md`. Should I update its status to `specified`?"

When displaying items, always use their stable ID (e.g., SCHED-0001) rather than position numbers.

#### Reorder
Move items up or down in priority. Reference items by their ID (e.g., "Move SCHED-0004 above SCHED-0001"). Reorder the JSON array accordingly. IDs remain unchanged — only array position changes.

#### Update status
Change an item's status (reference by ID). Validate transitions using the item's `spec_folder` field:
- To `specified`: if `spec_folder` is set, check that `{spec_folder}/spec.md` exists. If `spec_folder` is not set, ask the user which spec folder this item corresponds to and offer to set it.
- To `planned`: if `spec_folder` is set, check that `{spec_folder}/plan.md` exists. If `spec_folder` is not set, ask the user.
- To `done`: no automated check, trust the user's judgment.
- Allow manual overrides if the user insists (the checks are guardrails, not gates).

When transitioning an item from `idea` to any other status, offer to set `spec_folder` if it is not already set:
> "This item doesn't have a spec_folder yet. Which spec folder does it correspond to? (e.g., specs/004-coverage-tools)"

#### Link spec folder
Set or update the `spec_folder` field on an item. This connects a roadmap item to its spec artifacts directory. Usage:
> "Link SCHED-0004 to specs/004-coverage-tools"

After setting, re-run the render script to update artifact links in ROADMAP.md.

#### Add/remove dependency
Add or remove a dependency between items:
> "SCHED-0004 depends on SCHED-0003"
> "Remove dependency of SCHED-0004 on SCHED-0003"

Validate that the referenced ID exists. After modification, re-run the render script.

#### Remove
Remove an item from the roadmap (reference by ID). Confirm with the user before deleting. The removed item's ID is never reused.

#### Next
Suggest which `idea` item to spec next based on its position in the array (earlier = higher priority). Consider dependencies: if an `idea` item depends on items that are not yet `done` or `planned`, flag this but do not block the suggestion. Present the item's ID, title, and fields. Offer to hand off to `/speckit.specify`. If the item has no `primer`, offer to run `/speckit-specify-primer` first to shape one.

---

## Migration (v1 to v2)

If Phase 0 detects a `specs/roadmap.json` without a `key` field or with items missing `id` fields, offer to migrate:

1. **Ask for the project key**: "Your roadmap doesn't have a project key yet. This is a short uppercase prefix for item IDs (e.g., SCHED, PROJ, APP). What key would you like to use?"

2. **Assign IDs**: For each existing item, assign `{key}-{4-digit sequence}` based on current array position (first item gets 0001, second gets 0002, etc.).

3. **Detect spec_folder**: For each item, check if a `specs/` subdirectory matches the item's position or title. If a likely match is found, offer to set `spec_folder`:
   > "Item PROJ-0003 (MCP Server Bootstrap) looks like it corresponds to `specs/003-mcp-server/`. Set spec_folder?"

4. **Write and render**: Write the migrated roadmap.json and re-render.

Present the full migration plan to the user before making changes.

---

## Quality Signals

A good roadmap item should:
- Be scoped to a **single, independently specifiable** feature
- Describe **user value**, not implementation details
- Have **clear boundaries** (what's in and what's out for this item)
- Be **distinct** from other roadmap items (minimal overlap)

A roadmap item is NOT ready if:
- It's so broad that it would produce a spec with 10+ user stories
- It overlaps significantly with another item (candidates for merging)
- It describes a technical task rather than a user-facing feature
