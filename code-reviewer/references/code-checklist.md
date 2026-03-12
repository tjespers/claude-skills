# Code Review Checklist (Spec Compliance)

Review dimensions for implementation PRs. Focus: does the code deliver what the spec promises? Only report issues, not passing checks.

## FR Coverage

- Every FR from spec.md has corresponding implementation in the diff
- No FR left unimplemented without explicit deferral in spec or tasks.md
- FRs marked MUST are fully implemented, not partially
- FRs marked SHOULD are implemented or explicitly noted as deferred

## Design Decision Compliance

- Code follows each numbered design decision (D1, D2, ...) from plan.md
- File locations match the project structure declared in plan.md
- New files appear where the plan says they should (layer, namespace, directory)
- No design decisions contradicted without documented rationale

## Architecture & Layer Discipline

- Dependencies flow inward only (hexagonal: Filament → Application → Domain/Engine ← Infrastructure)
- AI agents in `src/AI/{Domain}/Agents/`, not in Application or Filament
- Application handlers in `src/Application/`, not in Filament actions
- Filament actions delegate to Application handlers — no direct Eloquent or Agent calls
- Domain/Engine layers have no outward dependencies (no imports from Infrastructure, AI, or Filament)
- New Eloquent models in `src/Infrastructure/`, not in Domain

## Entity & DTO Alignment

- Key entities from spec match classes/models in code
- DTO fields match the spec's entity attribute lists
- Enum cases match spec values (e.g., HIGH/LOW confidence)
- JSON structures match data-model.md schemas

## Phantom Feature Detection

- No code implements capabilities not described in spec or plan
- No extra API endpoints, routes, or commands beyond spec scope
- No gold-plating: additional config options, feature flags, or optional behaviors not in spec
- Deferred items (struck-through FRs, "v2" items) are NOT implemented

## Constitution Compliance

- `declare(strict_types=1)` on all new PHP files
- Conventional commit scopes match `.commitlintrc.yml`
- Test strategy matches plan (Pest vs Behat vs both)
- PHPStan compatibility (no `mixed` types, proper generics)
