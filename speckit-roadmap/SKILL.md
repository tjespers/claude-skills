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
  version: 1.0.0
---

# Speckit Roadmap

## Phase 0: Load Context

Silently load project context before engaging the user:

1. **Roadmap** — Read `specs/roadmap.json` if it exists. Note existing items, their statuses, and ordering.
2. **Constitution** — Read `.specify/memory/constitution.md` if it exists. Note principles and constraints that may affect decomposition or prioritization.
3. **Existing specs** — List `specs/` directories. Cross-reference with roadmap items to detect stale statuses (e.g., a `specs/###-feature-name/` folder exists but the corresponding roadmap item is still marked `idea`).
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

   > **Item N — [Title]:**
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
> **1. [Title]**
> **Who:** ... | **Why:** ...
> **Goals:** ... | **Non-goals:** ...
>
> **2. [Title]**
> **Who:** ... | **Why:** ...
> **Goals:** ... | **Non-goals:** ...

Ask the user to confirm before writing.

### Phase 3: Write and Render

After user confirmation, write the items to `specs/roadmap.json` and render.

#### JSON schema

`specs/roadmap.json` structure:

```json
{
  "items": [
    {
      "title": "Short descriptive name",
      "status": "idea",
      "who": "Who benefits from this feature.",
      "why": "What problem it solves or opportunity it creates.",
      "goals": ["Outcome 1", "Outcome 2"],
      "non_goals": ["Explicitly excluded 1", "Explicitly excluded 2"],
      "primer": "(optional) Natural language description ready for /speckit.specify"
    }
  ]
}
```

Array order = priority order (first = highest priority).

Status values map to the speckit workflow:
- `idea` — captured on the roadmap, not yet specified
- `specified` — `/speckit.specify` has been run, `spec.md` exists
- `planned` — `/speckit.plan` has been run, `plan.md` exists
- `done` — implemented and shipped

#### Writing the roadmap

- **New roadmap**: Create `specs/roadmap.json` with the items array.
- **Existing roadmap**: Read the current file, append new items to the array, write back.

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
Display the current roadmap with statuses. If stale statuses were detected in Phase 0, surface them:

> "I noticed [Title] is still marked as `idea` but a spec folder (`specs/###-feature-name/`) already exists. Should I update its status to `specified`?"

#### Reorder
Move items up or down in priority. Ask which item to move and where. Reorder the JSON array accordingly.

#### Update status
Change an item's status. Validate transitions:
- To `specified`: check that a matching `specs/###-feature-name/spec.md` exists
- To `planned`: check that a matching `specs/###-feature-name/plan.md` exists
- To `done`: no automated check, trust the user's judgment
- Allow manual overrides if the user insists (the checks are guardrails, not gates)

#### Remove
Remove an item from the roadmap. Confirm with the user before deleting.

#### Next
Suggest which `idea` item to spec next based on its position in the array (earlier = higher priority). Present the item's fields and offer to hand off to `/speckit.specify`. If the item has no `primer`, offer to run `/speckit-specify-primer` first to shape one.

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
