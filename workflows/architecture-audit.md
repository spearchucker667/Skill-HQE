# Architecture Audit Workflow

The `architecture` audit workflow (`/HQE architecture`) assesses structural design, component coupling, boundary enforcement, data flows, and long-term maintainability.

## Objective

Evaluate whether the repository's structure supports correctness, security, reliability, and evolution. Identify boundary leaks, layering violations, rigid abstractions, and state-management hazards. Produce actionable, evidence-backed architectural findings without prescribing speculative rewrites.

## Trigger Conditions

- User invokes `/HQE architecture`.
- A major feature, refactor, or new subsystem is being introduced.
- Recurring cross-module bugs suggest architectural coupling problems.
- Scaling, performance, or reliability concerns trace back to structural decisions.
- The codebase has grown beyond its original design and needs a health check.

## Execution Model

1. **Phase 0: Orientation & Subsystem Map**
   - Discover languages, frameworks, top-level directories, modules, and public entrypoints.
   - Distinguish first-party source from generated, vendored, build, and binary files.
   - **Exit criteria**: Subsystem inventory and coverage plan.

2. **Phase 1: Boundary & Coupling Analysis**
   - Identify public versus internal APIs.
   - Detect modules importing from private internals of other modules.
   - Check for circular dependencies and unstable abstraction leakage.
   - **Exit criteria**: Coupling matrix and boundary-violation candidates.

3. **Phase 2: Layering & State Review**
   - Verify presentation/UI layers do not bypass domain services to call databases or external systems directly.
   - Inspect mutable global state, shared singletons, and lifecycle management.
   - **Exit criteria**: Layering violation and state-management findings.

4. **Phase 3: Contract & Versioning Review**
   - Review API schemas, serialization contracts, and backward-compatibility guarantees.
   - Check that versioning strategies are explicit and respected.
   - **Exit criteria**: Contract drift or compatibility risks documented.

5. **Phase 4: Extensibility vs Overengineering**
   - Identify premature abstraction, unused interfaces, rigid boilerplate, and speculative generalization.
   - Balance extensibility needs against change budget and readability.
   - **Exit criteria**: Technical-debt candidates with impact estimates.

6. **Phase 5: Cross-Cutting Synthesis**
   - Correlate architecture findings with security, reliability, and performance observations.
   - Group symptoms that share a root structural cause.
   - **Exit criteria**: Consolidated root-cause findings.

7. **Phase 6: Remediation Planning & Artifacts**
   - Design minimal, safe remediation paths. Flag any user-visible behavior change with `[BEHAVIOR CHANGE]`.
   - Emit architecture audit artifacts.
   - **Exit criteria**: Deliverables written and pre-delivery gates satisfied.

## Required Controls / Checks

- Enforce module boundaries; public APIs must not leak private implementation details.
- Verify layering: UI/presentation → domain/service → data access → external I/O.
- Inspect mutable global state for synchronization and lifecycle hazards.
- Validate schema/API contracts for backward compatibility.
- Cite exact file paths, line numbers, and code snippets for every structural claim.
- Avoid full-system rewrites; prefer targeted refactors justified by evidence.
- Any intentional interface change requires `[BEHAVIOR CHANGE]` justification and approval.

## Artifact Outputs

Use the **Standard** output profile for subsystem audits and the **Exhaustive** profile for repository-wide architecture reviews.

- `HQE_REPORT.md` (architecture section and executive summary)
- `HQE_FINDINGS.json`
- `HQE_PATTERN_FINDINGS.md`
- `HQE_RELIABILITY.md`
- `HQE_MASTER_TODO.md`
- `HQE_UNKNOWNS.md`
- `HQE_CONFIDENCE.md`
- `HQE_RUN_MANIFEST.json`
- `HQE_SESSION_LOG.json`
- `HQE_HANDOFF.md` (when remediation is requested)

## Stop-the-Line Conditions

Halt normal audit flow and invoke `workflows/incident-response.md` if the architecture review reveals:

- A structural design that commits or exposes active credentials by default.
- A critical security boundary that is fundamentally absent (e.g., no authentication on an externally exposed admin interface).
- A design pattern that guarantees unrecoverable data loss under normal operation.

## Confidence Model Reminders

Tag every major claim:

- `[FACT]` — Directly verified by code, import graph, or build output.
- `[INFERENCE]` — Strongly supported structural deduction.
- `[HYPOTHESIS]` — Plausible architectural risk that requires deeper validation.
- `[NEEDS_VERIFICATION]` — Insufficient evidence; do not present as a confirmed finding.

Architectural opinions must be grounded in concrete code evidence, not aesthetic preference.
