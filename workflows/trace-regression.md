# Workflow: Multi-Hop Execution Trace & Regression Isolation

This workflow defines the procedure for tracing subtle behavior regressions across multiple subsystems or git revisions.

---

## Phase 1: Invariant & Baseline Definition
1. **Define Prior Behavior**:
   - Establish what the system previously returned or did (the expected invariant).
2. **Define Current Divergence**:
   - Record the exact unexpected result or state drift observed in the current version.
3. **Isolate Scope**:
   - Identify candidate commits, PR merges, or recently modified modules using `git log` and `git diff`.

---

## Phase 2: Multi-Hop Call-Graph Tracing
1. **Entrypoint Mapping**:
   - Identify the user entrypoint (CLI command, HTTP endpoint, event handler).
2. **Hop-by-Hop Data Flow Tracing**:
   - Trace arguments as they pass across module boundaries:
     - Hop 1: Controller / Entry Handler
     - Hop 2: Middleware / Validation layer
     - Hop 3: Core Service / Business logic
     - Hop 4: Persistence / External client / Serializer
3. **Locate Divergence Point**:
   - Identify the exact transformation step where data deviates from the historical contract.

---

## Phase 3: Bisect & Commit Analysis
1. **Git Bisect / Commit Audit**:
   - If git history is available, inspect commits touching the affected module.
   - Analyze diff hunks for unintended side-effects, altered default parameters, or subtle type coercions.
2. **Tag Regression Finding**:
   - Classify as `HQE-BUG-xxx` or `HQE-REL-xxx` with explicit `[BEHAVIOR CHANGE]` tags if intentionality is ambiguous.

---

## Phase 4: Remediation & Regression Test
1. **Construct End-to-End Regression Test**:
   - Write a regression test verifying the end-to-end multi-hop invariant.
2. **Implement Minimal Fix**:
   - Restore expected behavior within the $\le 5$ file change budget.
3. **Verify Contract Stability**:
   - Run both new regression test and all existing unit/integration test suites.
