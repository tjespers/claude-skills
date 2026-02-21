---
name: speckit-specify-primer
description: >
  Interactive brainstorming companion for spec-kit users. Helps shape and refine
  a feature idea into a high-quality natural language description before feeding it
  to /speckit.specify. Use this skill when: (1) a user wants to brainstorm or think
  through a feature before specifying it, (2) a user's feature description is too
  vague, too implementation-focused, or lacks scope boundaries, (3) you proactively
  detect the user is about to run /speckit.specify with a rough or problematic idea.
license: Apache-2.0
metadata:
  author: Tim Jespers <git@tjespers.dev>
  version: 1.0.0
---

# Speckit Specify Primer

Transform a rough feature idea into well-crafted input for `/speckit.specify` through progressive refinement. Address three common pitfalls: descriptions that are too vague, too implementation-focused, or missing clear scope boundaries.

## Phase 0: Gather Project Context

Silently load project context before engaging the user:

1. **Constitution** — Read `.specify/memory/constitution.md` if it exists. Note principles and constraints.
2. **Existing specs** — List `specs/` or `.specify/specs/` directories. Read spec files if relevant to the user's idea.
3. **Codebase awareness** — Note language, framework, and structure from agent context files (CLAUDE.md, plan files) or quick inspection.

Do not report this to the user unless asked. Use it to ask smarter questions and catch conflicts early.

## Phase 1: Seed

Ask the user to describe their feature however feels natural. If they already provided a description when invoking the skill, use that as the seed — do not ask them to repeat themselves.

After receiving the seed, produce a **first draft** (2-4 sentences) capturing your understanding:

> **Draft v1:**
> [natural language description]

Then identify the most important gaps using your internal coverage checklist (Phase 2) and ask 2-3 targeted questions to address them.

## Phase 2: Refine

Use these lenses as an internal checklist to ensure coverage. Do NOT present them as a rigid framework to the user — weave them naturally into the conversation.

### Coverage Lenses

- **Users** — Who are the actors? What roles, permissions, or personas are involved?
- **Problem** — What pain point or opportunity does this address? Why now?
- **Behavior** — What should happen from the user's perspective? What are the key flows?
- **Scope boundary** — What is explicitly OUT of scope? Where does this feature end?
- **Success** — How will we know this works? What does success look like for the user?
- **Edge cases** — What happens at the boundaries? Error states, empty states, limits?
- **Constraints** — Any known limitations from the constitution, existing architecture, or business rules?

### Refinement Loop

Each round:

1. Review the user's latest input against the coverage lenses
2. Identify the 2-3 most impactful gaps that remain
3. Ask targeted questions — prefer multiple-choice with a recommended option where possible, to reduce cognitive load
4. Produce an updated draft incorporating the new information

Present the updated draft as:

> **Draft v[N]:**
> [natural language description]

### Adaptive Depth

- **Simple features** (single actor, clear behavior, narrow scope): 1-2 rounds should suffice
- **Medium features** (multiple flows, some ambiguity): 2-3 rounds
- **Complex features** (multiple actors, integrations, unclear boundaries): 3-5 rounds

Signal when you believe the description is ready. Tell the user which lenses are well-covered and if any remain thin (letting them decide whether to refine further or proceed).

### Steering Away from Implementation

If the user starts describing HOW something should be built (technologies, APIs, database schemas, architecture), gently redirect:

- Acknowledge their technical thinking
- Reframe in terms of user needs and behavior: "So from the user's perspective, what you're describing is [behavior]. Let's capture that intent — the /speckit.specify command will handle the technical framing later."
- If implementation details reveal important constraints (e.g., "we must use the existing auth system"), capture those as constraints, not as requirements

### Catching Conflicts

Use the project context from Phase 0 to:
- Flag when the proposed feature overlaps with or contradicts an existing spec
- Note when the feature would conflict with a constitution principle
- Highlight when scope is creeping into territory covered by another feature

Raise these as observations, not blockers. The user decides how to proceed.

## Phase 3: Finalize and Hand Off

When the description is ready (user confirms, or you've signaled readiness and the user agrees):

### Default: Direct Handoff
Invoke `/speckit.specify` with the final description. Frame it as:

"Here's the final description I'll pass to `/speckit.specify`:"

> **Final:**
> [natural language description]

Then proceed to run `/speckit.specify [description]`.

### Alternative: Text Block
If the user explicitly asked for a text block instead of direct handoff, present the final description for them to copy and use at their own pace.

## Quality Signals

A good feature description for `/speckit.specify` should:
- Be written in terms of **user needs and behavior**, not technical implementation
- Clearly identify **who** the users are
- Describe **what** should happen and **why** it matters
- Have **clear scope boundaries** (what's in, what's out)
- Be **specific enough** that two people reading it would build roughly the same thing
- Be **concise** — typically 3-8 sentences for a well-scoped feature

A description is NOT ready if:
- It reads like a technical design document
- It uses phrases like "add a [technology]" without explaining the user need
- The scope is unbounded ("and also it should handle...")
- Key actors or flows are ambiguous
- Someone unfamiliar with the project couldn't understand the intent
