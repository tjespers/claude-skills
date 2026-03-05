# Spec Review Checklist

Review dimensions for `spec.md` files. Each dimension produces findings — only report issues, not passing checks.

## Structure & Completeness

- All mandatory sections present: `User Scenarios & Testing`, `Requirements`, `Success Criteria`
- Metadata block complete: Feature Branch, Created, Status, Input
- Assumptions section present
- Edge Cases section present within User Scenarios

## Internal Consistency

- Every FR has at least one acceptance scenario that exercises it
- Every acceptance scenario maps to at least one FR
- Success criteria are achievable given the functional requirements
- Key entities match the entities referenced in FRs and user stories
- Priority ordering is logical (P1 = core value, P2+ = enhancements)

## Cross-Reference Validity

- SCHEDULING-N references point to real tickets (check via Jira if accessible, otherwise flag for manual verification)
- Dependency specs/features referenced actually exist
- Feature branch name matches the spec's declared branch
- Spec number in directory matches Jira ticket number (if conventions require 1:1 mapping)

## Requirement Quality

- FRs use RFC 2119 keywords (MUST/SHOULD/MAY) consistently and in ALL CAPS
- FRs are numbered sequentially (FR-001, FR-002, ...) with no gaps
- SCs are numbered sequentially (SC-001, SC-002, ...) with no gaps
- Each FR is testable — can you write a concrete test for it?
- No implementation details leak into FRs (languages, frameworks, specific APIs)
- No vague requirements ("the system should be fast", "user-friendly interface")

## Acceptance Scenarios

- Follow Given/When/Then format with bold keywords
- Cover happy path, error path, and boundary conditions
- Each scenario is independently testable
- No scenario depends on another scenario's state

## Scope & Boundaries

- Non-goals are explicit (what this feature does NOT do)
- Dependencies are listed with their current status
- No scope creep — requirements stay within the declared boundaries
- If Scope Boundaries section exists, in-scope/out-of-scope items are consistent with the rest of the spec
