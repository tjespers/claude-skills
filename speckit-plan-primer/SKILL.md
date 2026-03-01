---
name: speckit-plan-primer
description: >
  Interactive brainstorming companion for spec-kit users. Helps shape technical
  architecture choices and stack decisions into well-crafted input for /speckit.plan.
  Use this skill when: (1) a user wants to think through their technical approach before
  planning, (2) a user's technical description is too vague, re-states user requirements
  instead of technical choices, or misses key dimensions like performance/scale,
  (3) you proactively detect the user is about to run /speckit.plan with incomplete
  or unfocused technical input.
license: Apache-2.0
metadata:
  author: Tim Jespers <git@tjespers.dev>
  version: 1.0.0
---

# Speckit Plan Primer

Transform rough technical thinking into well-crafted input for `/speckit.plan` through progressive refinement. Address three common pitfalls: descriptions that are too vague ("use modern tech"), that re-state user requirements instead of technical choices, or that miss key technical dimensions like performance targets, scale expectations, or platform constraints.

## Phase 0: Gather Project Context

Silently load project context before engaging the user:

1. **Constitution** — Read `.specify/memory/constitution.md` if it exists. Note principles and technical constraints that will gate the plan.
2. **Feature spec** — Locate and read the current feature's `spec.md` (from `specs/` based on the current branch, or ask the user which feature). This is critical — the plan must serve the spec's requirements. Note key entities, non-functional requirements, success criteria, and any constraints stated in the spec.
3. **Existing plan artifacts** — Check if `plan.md`, `research.md`, or other plan artifacts already exist (indicating a re-plan or iteration).
4. **Codebase awareness** — Note language, framework, and structure from agent context files (CLAUDE.md, plan files) or quick inspection. Existing technology choices in the codebase are strong signals.

Do not report this to the user unless asked. Use it to ask smarter questions and catch misalignments early.

## Phase 1: Seed

Ask the user to describe their technical approach however feels natural. If they already provided a description when invoking the skill, use that as the seed — do not ask them to repeat themselves.

After receiving the seed, produce a **first draft** capturing your understanding of their technical choices:

> **Draft v1:**
> [technical description suitable for /speckit.plan]

Then identify the most important gaps using your internal coverage checklist (Phase 2) and ask 2-3 targeted questions to address them.

## Phase 2: Refine

Use these lenses as an internal checklist to ensure coverage. Do NOT present them as a rigid framework to the user — weave them naturally into the conversation.

### Coverage Lenses

- **Language & Runtime** — What programming language and version? What runtime or platform SDK?
- **Frameworks & Dependencies** — What are the primary frameworks? What key libraries? Prefer naming specific packages over generic categories.
- **Storage** — What database, file system, or persistence strategy? ORM or query builder? Migration approach?
- **Architecture** — What structural pattern? (monolith, microservices, serverless, CLI, library, etc.) How are components organized?
- **Interfaces** — What external interfaces exist? REST API, GraphQL, CLI, UI framework? What protocols?
- **Testing** — What testing framework and strategy? Unit, integration, e2e? What coverage expectations?
- **Platform & Deployment** — Where does this run? (cloud, edge, embedded, desktop, mobile, browser) What OS/environment constraints?
- **Performance & Scale** — What are the concrete targets? (latency p95, throughput, memory budget, concurrent users) Vague words like "fast" need numbers.
- **Constraints** — What's non-negotiable? (existing auth system, specific cloud provider, compliance requirements, offline capability, budget limits)

### Refinement Loop

Each round:

1. Review the user's latest input against the coverage lenses
2. Cross-check against the feature spec — are their technical choices compatible with the spec's requirements, entities, and non-functional attributes?
3. Identify the 2-3 most impactful gaps that remain
4. Ask targeted questions — prefer multiple-choice with a recommended option where possible, especially when the codebase or constitution suggests a clear direction
5. Produce an updated draft incorporating the new information

Present the updated draft as:

> **Draft v[N]:**
> [technical description suitable for /speckit.plan]

### Adaptive Depth

- **Narrow features** (single component, known stack, clear constraints): 1-2 rounds should suffice
- **Medium features** (multiple components, some undecided choices): 2-3 rounds
- **Complex features** (new stack, distributed systems, multiple integration points): 3-5 rounds

Signal when you believe the technical description is ready. Tell the user which lenses are well-covered and if any remain thin (letting them decide whether to refine further or proceed).

### Spec Misalignment Detection

If the user starts describing WHAT the feature should do (user stories, behavior, flows) rather than HOW to build it, treat this as a signal — not just a formatting issue.

**Severity assessment:**

- **Incidental context-setting** — A single passing reference to user behavior that naturally leads to a technical question. Extract the constraint and continue. Example: "it needs to work offline" → capture as a technical constraint.
- **Persistent spec-level thinking** — The user keeps returning to user needs, flows, or requirements across multiple exchanges. This suggests the spec doesn't fully capture their mental model of the feature, or they've evolved their thinking since the spec was written.
- **Direct contradiction** — The user describes behavior or scope that conflicts with what's in the current `spec.md`. The spec is out of date or incomplete.

**For incidental cases**, gently reframe toward technical decisions:
- "That requirement tells me we need [technical capability]. What's your thinking on how to achieve that — for example, [option A] vs [option B]?"

**For persistent or contradictory cases**, surface the misalignment and offer a reroute:
- Explain what you're observing: "It sounds like your vision for this feature has moved beyond what the current spec captures — you're describing [behavior/scope] that isn't reflected in `spec.md`."
- Recommend addressing the spec first: "Planning on top of a spec that doesn't match your intent will produce a plan that needs rework. Want to take a detour and tighten the spec first?"
- Offer concrete options:
  1. **Reroute to spec refinement** — Hand off to `/speckit-refine` (or `/speckit.clarify` directly if the gaps are narrow), carrying forward what the user has shared so nothing is lost. Frame what they've said as refinement context.
  2. **Reroute to specify-primer** — If the gaps are fundamental (new scope, new actors, rethought flows), hand off to `/speckit-specify-primer` to reshape the feature description before re-specifying.
  3. **Continue anyway** — The user may be aware of the gap and choose to plan against the current spec regardless. Respect this, but note the risk.

**When rerouting**, preserve context by summarizing the spec-level insights the user has shared, so the receiving skill can pick up without the user repeating themselves.

### Turning Vagueness into Specifics

When the user gives vague input, don't accept it — help them get specific:

- "Modern tech stack" → "What language are you most productive in? Does the existing codebase constrain this?"
- "Fast" → "What's the latency budget? Sub-100ms? Sub-1s? What's the expected load?"
- "Scalable" → "What's the realistic user count for v1? For the next year? Are we talking 100 or 100,000?"
- "Good database" → "What's the data shape — relational, document, graph? Read-heavy or write-heavy? How much data?"

### Catching Misalignments

Use the project context from Phase 0 to:
- Flag when technical choices conflict with the feature spec's requirements (e.g., choosing an eventually-consistent database when the spec requires strong consistency)
- Note when choices contradict a constitution principle (e.g., choosing a heavy framework when the constitution mandates minimal dependencies)
- Highlight when the codebase already uses a different technology for the same concern (e.g., proposing SQLAlchemy when the project already uses Prisma)
- Surface when non-functional requirements from the spec aren't addressed by any technical choice

Raise these as observations, not blockers. The user decides how to proceed.

## Phase 3: Finalize and Hand Off

When the description is ready (user confirms, or you've signaled readiness and the user agrees):

### Default: Direct Handoff
Invoke `/speckit.plan` with the final description. Frame it as:

"Here's the technical description I'll pass to `/speckit.plan`:"

> **Final:**
> [technical description]

Then proceed to run `/speckit.plan [description]`.

### Alternative: Text Block
If the user explicitly asked for a text block instead of direct handoff, present the final description for them to copy and use at their own pace.

## Quality Signals

A good technical description for `/speckit.plan` should:
- **Name specific technologies** — language versions, framework names, database engines, not generic categories
- **State concrete constraints** — numbers for performance, scale, and resource budgets, not adjectives
- **Cover the full stack** — from storage through business logic to interfaces/UI, with testing strategy
- **Align with the spec** — technical choices should serve the spec's requirements and non-functional attributes
- **Respect the codebase** — build on existing technology choices unless there's a clear reason to diverge
- **Be architecture-level** — describe component structure and key technical decisions, not implementation details like class names or function signatures

A description is NOT ready if:
- It reads like a feature description ("users can upload photos and organize them") — that belongs in the spec
- It uses vague qualifiers without numbers ("fast", "scalable", "modern", "efficient")
- Key dimensions are missing (no storage strategy, no testing approach, no performance targets)
- It contradicts the feature spec's requirements or the project constitution
- It ignores existing codebase conventions without acknowledging the divergence
