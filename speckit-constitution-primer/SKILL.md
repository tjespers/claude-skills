---
name: speckit-constitution-primer
description: >
  Interactive brainstorming companion for spec-kit users. Helps shape project
  principles and governance priorities into well-crafted input for /speckit.constitution.
  Use this skill when: (1) a user wants to think through their project principles before
  running /speckit.constitution, (2) a user's constitution input reads like literal rules
  that the agent will just copy-paste without examining the codebase, (3) you proactively
  detect the user is about to run /speckit.constitution with generic or pre-baked input,
  (4) a user says "let's write a constitution" or "set up speckit for this project".
license: Apache-2.0
metadata:
  author: Tim Jespers <git@tjespers.dev>
  version: 1.0.0
---

# Speckit Constitution Primer

Transform rough ideas about project values into well-crafted input for `/speckit.constitution` through progressive refinement. Address the central pitfall: when users hand the constitution command literal principles ("all functions must be under 20 lines", "100% test coverage"), the agent tends to just adopt them without analyzing the codebase. The primer helps users express priorities and areas of emphasis instead, so the constitution command actually investigates the project and derives grounded, context-aware principles.

## Phase 0: Gather Project Context

Silently load project context before engaging the user:

1. **Existing constitution** — Read `.specify/memory/constitution.md` if it exists. This may be a re-constitution or iteration — note what's already established and whether the user likely wants to revise or start fresh.
2. **Codebase awareness** — Note language, framework, and structure from agent context files (CLAUDE.md, plan files) or quick inspection. Existing patterns in the codebase are strong signals of implicit values.
3. **Existing specs** — Check if `specs/` or `.specify/specs/` exist. A project with ongoing specs is in a different place than a fresh setup.
4. **Development artifacts** — Glance at CI config, linting config, test setup, and dependency manifests. These reveal values already embedded in the project (e.g., a strict ESLint config signals a team that values consistency; a comprehensive test suite signals testing culture).

Do not report this to the user unless asked. Use it to ask smarter questions and catch misalignments early.

## Phase 1: Seed

Ask the user to describe what matters most for this project — what kind of software they're building, what quality attributes they care about, what their non-negotiables are. If they already provided context when invoking the skill, use that as the seed — do not ask them to repeat themselves.

After receiving the seed, produce a **first draft** framed as directional input for the constitution command — areas of emphasis, priorities, and constraints — NOT as literal principles or rules:

> **Draft v1:**
> [directional input for /speckit.constitution]

Then identify the most important gaps using your internal coverage checklist (Phase 2) and ask 2-3 targeted questions to address them.

## Phase 2: Refine

Use these lenses as an internal checklist to ensure coverage. Do NOT present them as a rigid framework to the user — weave them naturally into the conversation.

### Coverage Lenses

- **Project Identity** — What kind of software is this? (library, application, service, CLI tool) Who uses it? What's the maturity stage? (greenfield, established, legacy modernization)
- **Code Quality Philosophy** — What does "good code" mean for this project? Where does the team sit on readability vs performance? Complexity tolerance? Convention preferences?
- **Testing Philosophy** — What level of confidence does the team need? Integration vs unit emphasis? What's the testing culture — TDD, post-hoc, pragmatic?
- **Architecture Values** — How should the system grow? Monolith vs modular? Coupling tolerance? What patterns does the team gravitate toward?
- **Performance & Resource Awareness** — Does performance matter critically or is it secondary to velocity? Any memory, CPU, or latency constraints?
- **User Experience Principles** — Consistency, accessibility, progressive disclosure? What UX values matter for the project's audience?
- **Security & Compliance** — Any regulatory requirements? Data sensitivity levels? Auth/authz philosophy?
- **Dependency Philosophy** — Lean vs batteries-included? Vendor lock-in tolerance? OSS licensing constraints?
- **Development Workflow** — Review culture, documentation expectations, deployment cadence, release philosophy?
- **Error Philosophy** — Fail fast vs resilient? How should the system handle and communicate failure? Observability expectations?

### Refinement Loop

Each round:

1. Review the user's latest input against the coverage lenses
2. Cross-check against the project context from Phase 0 — do the user's stated priorities align with what the codebase already reveals? Surface interesting tensions.
3. Identify the 2-3 most impactful gaps that remain
4. Ask targeted questions — prefer multiple-choice with a recommended option where possible, especially when the codebase or existing artifacts suggest a clear direction
5. Produce an updated draft incorporating the new information

Present the updated draft as:

> **Draft v[N]:**
> [directional input for /speckit.constitution]

### Adaptive Depth

- **Focused projects** (clear domain, small team, established values): 1-2 rounds should suffice
- **Medium projects** (some competing priorities to resolve, multiple stakeholders): 2-3 rounds
- **Complex projects** (regulatory concerns, greenfield with many unknowns, large team): 3-5 rounds

Signal when you believe the input is ready. Tell the user which lenses are well-covered and if any remain thin (letting them decide whether to refine further or proceed).

### Steering Away from Literal Principles

This is the most important aspect of the primer. If the user starts dictating specific rules ("all functions must be under 20 lines", "100% test coverage required", "never use any"), gently redirect:

- Acknowledge the intent behind the rule — there's always a real value underneath
- Reframe as a priority or direction: "It sounds like you value keeping code simple and scannable. Let's capture that priority — the `/speckit.constitution` command will examine the codebase and derive specific, grounded principles from that direction."
- If a rule reveals a genuine hard constraint (regulatory, contractual, organizational mandate), capture it explicitly as a constraint — those are different from principles and the constitution command should know about them

The reason this matters: when we hand pre-baked rules to the constitution command, it tends to just adopt them verbatim without analyzing the codebase. By framing our input as values and areas of focus, we get a much richer constitution that's actually grounded in the project's reality — its patterns, its tech stack, its existing conventions.

### Surfacing Codebase Tensions

Use the project context from Phase 0 to:
- Note when the user's stated priorities already show up in the codebase (reinforce: "the project already demonstrates this — the strict linting config and consistent naming suggest this is a team value worth codifying")
- Flag when stated priorities conflict with observable patterns (e.g., user says "minimal dependencies" but the project has 200+ npm packages — this is a tension worth naming, not a blocker)
- Highlight when the codebase reveals implicit values the user hasn't mentioned (e.g., a comprehensive CI pipeline suggests deployment reliability matters)

Raise these as observations, not blockers. The user decides how to proceed.

## Phase 3: Finalize and Hand Off

When the input is ready (user confirms, or you've signaled readiness and the user agrees):

### Default: Direct Handoff
Invoke `/speckit.constitution` with the final input. Frame it as:

"Here's what I'll pass to `/speckit.constitution`:"

> **Final:**
> [directional input — priorities, areas of emphasis, constraints]

Then proceed to run `/speckit.constitution [input]`.

### Alternative: Text Block
If the user explicitly asked for a text block instead of direct handoff, present the final input for them to copy and use at their own pace.

## Quality Signals

A good constitution input for `/speckit.constitution` should:
- Express **values and priorities**, not literal rules — guide the command to investigate and derive, not transcribe
- Identify **areas of emphasis** that tell the constitution command where to focus its analysis
- Include **hard constraints** only when they're genuinely non-negotiable (regulatory, contractual, organizational mandate)
- Reflect the **project's actual context** — its maturity, domain, tech stack, and audience
- Be **directional** — point the constitution command at what matters, trusting it to formulate specific principles grounded in the codebase
- Cover **multiple dimensions** — not just code quality, but also testing, architecture, UX, dependencies, and how the system should evolve

A constitution input is NOT ready if:
- It reads like a list of rules the agent will just copy-paste
- It's entirely generic ("write clean code, test everything, be secure") with nothing project-specific
- It ignores the project's actual technology, domain, or maturity level
- It's missing major dimensions (e.g., says nothing about testing, or nothing about how the system should grow)
- It contradicts observable patterns in the codebase without acknowledging the divergence
