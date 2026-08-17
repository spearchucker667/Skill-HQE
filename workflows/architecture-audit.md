# Architecture Audit Workflow

The `architecture` audit workflow (`/HQE architecture`) assesses structural design, component coupling, boundary enforcement, data flows, and long-term maintainability.

## 1. Objective

Evaluate whether the repository's structure supports correctness, security, reliability, and evolution. Identify boundary leaks, layering violations, rigid abstractions, and state-management hazards. Produce actionable, evidence-backed architectural findings without prescribing speculative rewrites.

## 2. Prerequisites

Before starting the architecture audit, confirm the following:

- [ ] Access to the full repository source, configuration files, build scripts, and dependency manifests.
- [ ] Access to API schemas, interface definitions, and module/package boundaries.
- [ ] A clean working directory or a defined scope of changed files for PR-based audits.
- [ ] `protocol/hqe-engineer.yaml` and `references/architecture-review.md` are available for reference.
- [ ] Schema validators in `scripts/` are runnable (`python3 scripts/validate_findings.py`, etc.).
- [ ] The change budget and output caps from `protocol/hqe-engineer.yaml` are known.

## 3. Entry Criteria

Begin this workflow when any of the following are true:

- User invokes `/HQE architecture`.
- A major feature, refactor, or new subsystem is being introduced.
- Recurring cross-module bugs suggest architectural coupling problems.
- Scaling, performance, or reliability concerns trace back to structural decisions.
- The codebase has grown beyond its original design and needs a health check.

## 4. Stop-the-Line Conditions

Immediately halt the normal audit flow and invoke [`workflows/incident-response.md`](incident-response.md) if the architecture review reveals:

- A structural design that commits or exposes active credentials by default.
- A critical security boundary that is fundamentally absent (e.g., no authentication on an externally exposed admin interface).
- A design pattern that guarantees unrecoverable data loss under normal operation.

Flag the triggering item as `STOP-THE-LINE: [issue]` in the session log and do not proceed with normal artifact generation until incident response is complete.

## 5. Execution Model

### Phase 0: Orientation & Subsystem Map

**Goal**: Establish a repository-grounded understanding of the structure before deep analysis.

1. **Inventory the stack**:
   - Identify languages, frameworks, runtime, package manager, test framework, and build system.
   - Classify directories as source, generated, vendored, config, test, or documentation.
2. **Map subsystems and components**:
   - Name each subsystem and summarize its responsibility in 1–2 lines.
   - Identify public entry points (HTTP routes/handlers, CLI commands, workers, webhooks, exported libraries).
   - Record each entry point with `file:line` or `anchor+grep`.
3. **Trace data flows**:
   - Document `input → validation → processing → persistence → output` for major flows.
   - Mark trust boundaries using `[Zone A] → [Zone B] via [mechanism]`.
4. **Classify files for coverage**:
   - Decide which files receive deep review, skim, or skip, with evidence-based reasons.

**Evidence to collect**:
- Repository inventory table (file counts, languages, frameworks).
- Subsystem/component map with responsibilities and entry points.
- Data-flow diagram or list with trust boundaries and validation points.
- Coverage classification (deep / skim / skipped) with rationale.

**Exit criteria**:
- [ ] A documented subsystem inventory exists.
- [ ] Every major subsystem has a locatable responsibility statement.
- [ ] Data flows and trust boundaries are anchored to code locations.

### Phase 1: Boundary & Coupling Analysis

**Goal**: Verify that components expose stable boundaries and do not leak internal details.

1. **Identify public versus internal APIs**:
   - List exported functions, classes, modules, and endpoints.
   - Verify that public surfaces are intentional and documented.
2. **Detect boundary violations**:
   - Find modules importing from private internals of other modules.
   - Flag circular dependencies and unstable abstraction leakage.
3. **Assess cohesion**:
   - Look for classes/modules with mixed responsibilities or scatterede logic.
   - Identify shotgun surgery candidates.

**Evidence to collect**:
- Public API inventory with `file:line` for each exported symbol.
- Coupling matrix showing which modules depend on which internals.
- Boundary-violation candidates with import snippets.

**Exit criteria**:
- [ ] Coupling matrix and boundary-violation candidates documented.
- [ ] Each violation is either a finding or justified as intentional.

### Phase 2: Layering & State Review

**Goal**: Verify that layers are respected and state is managed safely.

1. **Check layering**:
   - Confirm UI/presentation → domain/service → data access → external I/O ordering.
   - Flag presentation code that bypasses domain services to call databases or external systems directly.
2. **Inspect mutable global state**:
   - Locate shared singletons, global caches, module-level variables, and registries.
   - Check for synchronization, lifecycle management, and test isolation issues.
3. **Review side effects**:
   - Identify hidden I/O inside constructors, module import time, or property accessors.

**Evidence to collect**:
- Layering violation findings with code paths.
- State-management map showing shared mutable state and lifecycle owners.
- Code snippets for side-effect hotspots.

**Exit criteria**:
- [ ] Layering violation and state-management findings documented.
- [ ] Each finding cites the exact file path, line number, and relevant code snippet.

### Phase 3: Contract & Versioning Review

**Goal**: Verify that contracts between components are explicit and stable.

1. **Review API schemas**:
   - Compare request/response schemas, serialization formats, and interface definitions to their consumers.
   - Flag undocumented or implicit fields.
2. **Check versioning**:
   - Identify versioning strategies for APIs, databases, and migration scripts.
   - Verify backward-compatibility guarantees are respected.
3. **Inspect error contracts**:
   - Confirm error codes, exceptions, and response shapes are predictable and handled uniformly.

**Evidence to collect**:
- Contract drift or compatibility risk findings.
- Code snippets showing schema definitions and consumers.
- Versioning strategy summary with gaps.

**Exit criteria**:
- [ ] Contract drift or compatibility risks documented.
- [ ] Each risk is tagged with confidence and severity.

### Phase 4: Extensibility vs Overengineering

**Goal**: Identify abstraction debt and speculative complexity.

1. **Find premature abstraction**:
   - Look for unused interfaces, abstract base classes with one implementation, and indirection without benefit.
2. **Assess boilerplate and generalization**:
   - Flag rigid boilerplate that obscures behavior or speculative generalization unlikely to be used.
3. **Balance change budget**:
   - For each abstraction concern, estimate impact versus removal/refactor effort.
   - Recommend the smallest change that improves clarity.

**Evidence to collect**:
- Technical-debt candidates with impact estimates.
- Code snippets showing the abstraction and its usage sites.

**Exit criteria**:
- [ ] Technical-debt candidates are prioritized by blast radius and effort.
- [ ] No full-system rewrites are proposed without explicit justification.

### Phase 5: Cross-Cutting Synthesis

**Goal**: Correlate architecture findings with security, reliability, and performance observations.

1. **Group symptoms by root cause**:
   - Combine findings that share a structural origin (e.g., one boundary leak causing multiple bugs).
2. **Cross-reference other audits**:
   - Map architecture findings to security, performance, testing, and documentation findings.
3. **Prioritize by systemic impact**:
   - Rank findings by how many other problems they cause or enable.

**Evidence to collect**:
- Consolidated root-cause findings.
- Mapping from architectural findings to related findings in other categories.

**Exit criteria**:
- [ ] Related findings are consolidated under shared root causes.
- [ ] Prioritization reflects systemic impact, not local preference.

### Phase 6: Remediation Planning & Artifacts

**Goal**: Produce clean, consistent, and internally consistent deliverables.

1. **Deduplicate findings** by root cause.
2. **Design minimal, safe remediation paths**:
   - Prefer targeted refactors over broad rewrites.
   - Flag any user-visible behavior change with `[BEHAVIOR CHANGE]`.
3. **Emit architecture audit artifacts**.
4. **Validate** all JSON artifacts against schemas in `schemas/`.

**Evidence to collect**:
- Final artifact set.
- Schema-validation output.
- Confidence declaration and unknowns list.

**Exit criteria**:
- [ ] All deliverables written and pre-delivery gates satisfied.
- [ ] Schema validation passes.

## 6. Required Controls / Checks

- Enforce module boundaries; public APIs must not leak private implementation details.
- Verify layering: UI/presentation → domain/service → data access → external I/O.
- Inspect mutable global state for synchronization and lifecycle hazards.
- Validate schema/API contracts for backward compatibility.
- Cite exact file paths, line numbers, and code snippets for every structural claim.
- Avoid full-system rewrites; prefer targeted refactors justified by evidence.
- Any intentional interface change requires `[BEHAVIOR CHANGE]` justification and approval.
- Use finding IDs `MAINT-XXX` for maintainability issues and `REL-XXX` for reliability issues.

## 7. Artifact Outputs

Use the **Standard** output profile for subsystem audits and the **Exhaustive** profile for repository-wide architecture reviews.

- `HQE_REPORT.md` (architecture section and executive summary)
- `HQE_FINDINGS.json` (machine-readable architectural findings)
- `HQE_PATTERN_FINDINGS.md`
- `HQE_RELIABILITY.md`
- `HQE_MASTER_TODO.md`
- `HQE_UNKNOWNS.md`
- `HQE_CONFIDENCE.md`
- `HQE_RUN_MANIFEST.json`
- `HQE_SESSION_LOG.json`
- `HQE_HANDOFF.md` (when remediation is requested)

Validate machine-readable artifacts with:

```bash
python3 scripts/validate_findings.py HQE_FINDINGS.json
python3 scripts/validate_manifest.py HQE_RUN_MANIFEST.json
python3 scripts/validate_session_log.py HQE_SESSION_LOG.json
```

## 8. Exit Criteria

The architecture audit is complete when:

- [ ] All phases above have been executed or explicitly skipped with justification.
- [ ] Every architectural finding cites concrete code evidence.
- [ ] Behavior-changing recommendations are flagged with `[BEHAVIOR CHANGE]`.
- [ ] Artifacts are emitted and schema-validated.
- [ ] Stop-the-line conditions have been checked; if triggered, incident response has been invoked.
- [ ] The session log is updated with completed, in-progress, discovered, and reprioritized items.

## 9. Confidence Model Reminders

Tag every major claim:

- `[FACT]` — Directly verified by code, import graph, or build output.
- `[INFERENCE]` — Strongly supported structural deduction.
- `[HYPOTHESIS]` — Plausible architectural risk that requires deeper validation.
- `[NEEDS_VERIFICATION]` — Insufficient evidence; do not present as a confirmed finding.

Architectural opinions must be grounded in concrete code evidence, not aesthetic preference.
