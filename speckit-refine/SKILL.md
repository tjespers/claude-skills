---
name: speckit-refine
license: Apache-2.0
description: >
  Specification refinement companion for spec-kit users. Helps identify weak areas
  in an existing feature spec and shape focused input for /speckit.clarify. Use this
  skill when: (1) a user wants to refine or tighten a spec after /speckit.specify,
  (2) a user wants to revisit a spec after /speckit.plan exposed gaps, (3) you
  proactively detect a spec has thin or ambiguous areas before the user runs
  /speckit.clarify or /speckit.plan.
metadata:
  author: Tim Jespers <git@tjespers.dev>
  version: 1.0.0
---

# Speckit Refine

Help users identify what needs refinement in their feature spec and shape well-structured input for `/speckit.clarify`. Like a sprint refinement session — take what exists and lock down the details.

## Phase 0: Sync Branch and Load Context

Silently ensure we're working against the latest spec state before engaging the user.

### Step 1: Ensure correct feature branch

The spec files are located based on the current git branch (via `check-prerequisites.sh` → `common.sh` → `get_current_branch()`). The branch **must** be set before running prerequisites.

1. Run `git fetch --all --prune` to sync remote state.
2. Determine the target feature branch:
   - If the user specified a feature (by name or number), find the matching `###-feature-name` branch.
   - If already on a feature branch (`###-*` pattern), use the current branch.
   - If on `main` or another non-feature branch, list available feature branches from `specs/` directories and ask the user which spec to refine.
3. If the current branch doesn't match the target, run `git checkout <target-branch>` and pull latest: `git pull --ff-only` (suppress errors if no upstream is set).

### Step 2: Load project context

1. **Spec** — Run `.specify/scripts/bash/check-prerequisites.sh --json --paths-only` to locate the active feature. Read `spec.md`. Note which taxonomy areas (from `/speckit.clarify`'s categories) feel thin, ambiguous, or missing.
2. **Plan artifacts** (if they exist) — Read `plan.md`, `data-model.md`, files in `contracts/`, and `research.md`. Note gaps the planning phase may have exposed (e.g., entities referenced in data model but underspecified in spec, API contracts making assumptions not stated in requirements).
3. **Constitution** — Read `.specify/memory/constitution.md` if it exists. Note principles that should constrain refinement priorities.
4. **Existing clarifications** — Check if `spec.md` already has a `## Clarifications` section from prior `/speckit.clarify` runs. Note what's already been resolved.

Do not report context loading details to the user unless asked. Do inform them if a branch switch was made.

## Phase 1: Understand Refinement Intent

Two entry paths:

### User has a focus
If the user comes in with specific areas they want to refine (e.g., "I want to nail down the error handling" or "the data model feels fuzzy"), acknowledge their focus and use it to anchor the conversation.

### User wants discovery
If the user doesn't know where to start, offer 2-3 observations from your Phase 0 analysis — areas of the spec that look thinnest. Frame as:

> Based on the current spec, these areas could benefit from refinement:
> 1. [area] — [why it's thin, in one sentence]
> 2. [area] — [why it's thin, in one sentence]
> 3. [area] — [why it's thin, in one sentence]
>
> Which of these feels most important, or is there something else you'd rather focus on?

### Plan-aware observations

If plan artifacts exist, surface plan-exposed gaps specifically:
- Entities in the data model that lack clear spec requirements
- API contracts that assume behaviors not stated in the spec
- Research decisions that narrowed scope but weren't reflected back into the spec
- Technical context items marked as NEEDS CLARIFICATION in the plan

Frame these as: "The planning phase surfaced some areas where the spec could be tighter."

## Phase 2: Shape the Clarify Input

`/speckit.clarify` takes `$ARGUMENTS` as prioritization context. The goal is to craft this input so clarify focuses on what matters most.

### Refinement Dimensions

Use these internally to ensure the conversation covers the right ground. Do not present as a checklist — weave naturally.

- **What to clarify** — Which taxonomy categories need attention? (functional scope, data model, edge cases, non-functional attributes, etc.)
- **Why it matters** — What downstream risk does this ambiguity create? (misaligned tests, wrong data model, security gaps, scope creep)
- **Desired depth** — Does the user want to fully resolve these areas, or just reduce the biggest uncertainties?
- **Constraints on answers** — Are there known constraints that should steer the clarification? (e.g., "we know we can't exceed 100ms latency" — this should be in the prompt so clarify doesn't ask about it)
- **What NOT to clarify** — Areas the user explicitly considers good enough or wants to defer to implementation

### Conversation Flow

Each round:

1. Discuss the user's refinement priorities against the spec's actual gaps
2. Ask 1-3 targeted questions to sharpen focus or resolve ambiguity about what they want clarified
3. When the user asks for a preview, or when you've gathered enough to produce a meaningful draft, present it as:

> **Draft v[N]:**
> [structured natural language input for /speckit.clarify]

The draft should read as clear prioritization context — telling `/speckit.clarify` what to focus on, what constraints to respect, and what to skip.

### Adaptive Depth

- **Focused refinement** (user knows exactly what to tighten): 1-2 rounds, single clarify prompt
- **Moderate gaps** (2-3 areas need work): 2-3 rounds, single prompt covering priorities
- **Broad gaps** (spec is thin across many areas): 3-4 rounds, may produce 2-3 sequenced prompts for separate `/speckit.clarify` runs

When suggesting sequenced runs, explain the ordering rationale (e.g., "clarify the data model first since the edge cases depend on understanding the entities").

## Phase 3: Finalize and Hand Off

When the refinement priorities are clear:

### Default: Direct Handoff
Show the final input and invoke `/speckit.clarify`:

"Here's the refinement focus I'll pass to `/speckit.clarify`:"

> **Final:**
> [structured prioritization context]

Then run `/speckit.clarify [input]`.

For sequenced prompts, run the first one and tell the user to invoke `/speckit-refine` again (or run `/speckit.clarify` directly) for subsequent rounds.

### Alternative: Text Block
If the user explicitly asked for text output, present the final input(s) for them to use at their own pace.

## Quality Signals

A good refinement input for `/speckit.clarify` should:
- **Prioritize** — Tell clarify which taxonomy areas matter most, not just "refine everything"
- **Provide constraints** — Include known answers so clarify doesn't waste questions on resolved items
- **State the why** — Explain what downstream risk each ambiguity creates
- **Set boundaries** — Explicitly note what to skip or defer
- **Be specific** — Reference actual spec sections, requirements, or entities by name

A refinement input is NOT ready if:
- It's a generic "please clarify the spec" with no focus
- It duplicates areas already clarified in prior sessions
- It asks for implementation decisions that belong in `/speckit.plan`
- It doesn't reference the actual content of the spec
