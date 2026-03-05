# Plan Review Checklist

Review dimensions for `plan.md` files. Each dimension produces findings — only report issues, not passing checks.

## Structure & Completeness

- All sections present: Summary, Technical Context, Constitution Check, Project Structure, Key Design Decisions, Complexity Tracking
- Metadata links back to spec.md
- Technical Context fields complete: Language/Version, Primary Dependencies, Storage, Testing, Target Platform, Project Type, Performance Goals, Constraints

## Spec Alignment

- Every FR from the spec has corresponding implementation in the plan (file or design decision)
- No phantom features — plan doesn't implement things not in the spec
- Key entities from spec appear in the project structure (as models, DTOs, etc.)
- Design decisions don't contradict spec requirements

## Constitution Check

- Gate table present with all principles evaluated
- No FAIL statuses without justification
- Complexity tracking section addresses any concerns raised

## Project Structure

- Every file annotated with status: `(NEW)`, `(MODIFIED — <what>)`, or `(existing, not modified)`
- File locations follow project conventions (hexagonal architecture, namespace patterns)
- No orphan files — every file serves an FR or design decision
- Test files mirror source structure

## Design Decisions

- Numbered sequentially (D1, D2, ...)
- Each decision has rationale (why this choice over alternatives)
- Impact/trade-offs acknowledged where relevant
- No contradictions between decisions

## Technical Coherence

- Dependencies listed are compatible with each other and the project's existing stack
- Testing strategy covers the right layers (unit, integration, feature)
- Performance goals are realistic given the approach
