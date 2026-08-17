# Multi-Hop Execution Trace & Regression Isolation Workflow

The `trace` workflow (`/HQE trace`) defines the procedure for tracing subtle behavior regressions across multiple subsystems or git revisions. It combines call-graph tracing, git bisect, and invariant verification to isolate the exact change that broke a previously valid contract.

## 1. Objective

Identify the commit, function, or subsystem where a previously correct behavior diverged. Produce a deterministic reproduction, isolate the breaking change, and either restore the contract or document the regression with a verified fix plan.

## 2. Prerequisites

Before starting trace analysis, confirm the following:

- [ ] The expected prior behavior and the exact current divergence are documented.
- [ ] Git history is available for the affected paths.
- [ ] A reproduction command or test case exists (or can be constructed) that demonstrates the divergence.
- [ ] `protocol/hqe-engineer.yaml` and `references/reasoning-methodologies.md` are available for reference.
- [ ] Schema validators in `scripts/` are runnable (`python3 scripts/validate_findings.py`, etc.).

## 3. Entry Criteria

Begin this workflow when any of the following are true:

- User invokes `/HQE trace <symptom>`.
- A behavior regression spans multiple subsystems or hops.
- A previously passing integration or end-to-end test now fails after unrelated-looking changes.
- Output, serialization, or state differs from a known-good baseline with no obvious single-cause location.

## 4. Stop-the-Line Conditions

Immediately halt the trace workflow and invoke [`workflows/incident-response.md`](incident-response.md) if any of the following are found:

- Active credentials, API keys, tokens, or private keys committed or exposed in the regression range.
- A backdoor, malicious payload, or remote-code-execution path introduced in the regression range.
- A critical data-loss or data-corruption path reachable from the changed behavior.
- Evidence of active exploitation or unauthorized workflow modifications.

Flag the triggering item as `STOP-THE-LINE: [issue]` in the session log and do not proceed with normal artifact generation until incident response is complete.

## 5. Execution Model

### Phase 0: Invariant & Baseline Definition

**Goal**: Establish the contract that was broken and the scope of investigation.

1. **Define prior behavior**:
   - Establish what the system previously returned or did (the expected invariant).
   - Cite the last known-good commit, release, or test run if available.
2. **Define current divergence**:
   - Record the exact unexpected result or state drift observed in the current version.
3. **Isolate scope**:
   - Identify candidate commits, PR merges, or recently modified modules using `git log` and `git diff`.
   - List files touched in the suspected regression range.

**Evidence to collect**:
- Written invariant statement.
- Current divergence with exact output/state samples.
- Candidate commits and modified files.

**Exit criteria**:
- [ ] Expected invariant and observed divergence are documented.
- [ ] Candidate regression range is identified.

### Phase 1: Multi-Hop Call-Graph Tracing

**Goal**: Trace the behavior from user entrypoint through every subsystem that transforms it.

1. **Entrypoint mapping**:
   - Identify the user entrypoint (CLI command, HTTP endpoint, event handler, worker, cron job).
   - Record the entrypoint with `file:line`.
2. **Hop-by-hop data flow tracing**:
   - Trace arguments as they pass across module boundaries:
     - Hop 1: Controller / Entry Handler
     - Hop 2: Middleware / Validation layer
     - Hop 3: Core Service / Business logic
     - Hop 4: Persistence / External client / Serializer
   - Record each hop with `file:line` and transformation summary.
3. **Locate divergence point**:
   - Identify the exact transformation step where data deviates from the historical contract.

**Evidence to collect**:
- Multi-hop call graph with `file:line` for each hop.
- Transformation summary per hop.
- Candidate divergence point with snippet.

**Exit criteria**:
- [ ] Call graph from entrypoint to sink is documented.
- [ ] At least one candidate divergence point is identified.

### Phase 2: Bisect & Commit Analysis

**Goal**: Narrow the regression to a specific commit or change set.

1. **Git bisect / commit audit**:
   - If git history is available, use `git bisect` or inspect commits touching the affected module.
   - Analyze diff hunks for unintended side-effects, altered default parameters, subtle type coercions, missing null checks, or changed serialization.
2. **Tag regression finding**:
   - Classify as `HQE-BUG-xxx` or `HQE-REL-xxx` with explicit `[BEHAVIOR CHANGE]` tags if intentionality is ambiguous.
3. **Check anti-regression rule**:
   - If the regression was caused by a fix that removed or altered behavior, flag it per `protocol/hqe-engineer.yaml` anti_regression_rule.

**Evidence to collect**:
- Commit or range that introduced the regression.
- Diff hunk analysis showing the breaking change.
- Regression finding ID and classification.

**Exit criteria**:
- [ ] Breaking commit or change set is identified.
- [ ] Regression is classified and tagged.

### Phase 3: Remediation & Regression Test

**Goal**: Restore the expected behavior and prevent recurrence.

1. **Construct end-to-end regression test**:
   - Write a regression test verifying the end-to-end multi-hop invariant.
2. **Implement minimal fix**:
   - Restore expected behavior within the `<= 5` file change budget.
3. **Verify contract stability**:
   - Run both the new regression test and all existing unit/integration test suites.

**Evidence to collect**:
- Regression test with before/after results.
- Minimal fix diff.
- Full test suite results.

**Exit criteria**:
- [ ] Regression test exists and passes after the fix.
- [ ] Existing tests pass or failures are documented and accepted.

### Phase 4: Consolidation & Artifact Generation

**Goal**: Produce clean, consistent deliverables.

1. **Deduplicate findings** by root cause.
2. **Emit trace workflow artifacts**.
3. **Validate** all JSON artifacts against schemas in `schemas/`.
4. **Update the session log** with completed, in-progress, discovered, and reprioritized items.

**Evidence to collect**:
- Final artifact set.
- Schema-validation output.
- Confidence declaration and unknowns list.

**Exit criteria**:
- [ ] All deliverables written and pre-delivery gates satisfied.
- [ ] Schema validation passes.

## 6. Required Controls / Checks

- Every regression must cite the expected invariant and the observed divergence.
- The breaking change must be anchored to a commit, diff hunk, or `file:line`.
- Multi-hop traces must document every subsystem transformation.
- Regression tests must verify the end-to-end invariant, not just the final output.
- Keep the change budget to `<= 5` files unless explicitly justified.
- Flag intentional behavior changes with `[BEHAVIOR CHANGE]` and require explicit approval.
- Claims must cite exact file paths, line numbers, and 2–5 line snippets.
- Mark uncertain divergence points as `[NEEDS_VERIFICATION]`.

## 7. Artifact Outputs

- `HQE_REPORT.md` (regression summary, breaking commit, and fix)
- `HQE_FINDINGS.json`
- `HQE_RUN_MANIFEST.json`
- `HQE_SESSION_LOG.json`
- `HQE_PATTERN_FINDINGS.md` (if the trace reveals recurring anti-patterns)
- `HQE_HANDOFF.md` (when handing off remediation to another agent)

Validate machine-readable artifacts with:

```bash
python3 scripts/validate_findings.py HQE_FINDINGS.json
python3 scripts/validate_manifest.py HQE_RUN_MANIFEST.json
python3 scripts/validate_session_log.py HQE_SESSION_LOG.json
```

## 8. Exit Criteria

Trace analysis is complete when:

- [ ] All phases above have been executed or explicitly skipped with justification.
- [ ] The breaking commit or change set is identified.
- [ ] The regression is reproduced with a deterministic test.
- [ ] The fix is verified and no regressions are introduced.
- [ ] Artifacts are emitted and schema-validated.
- [ ] Stop-the-line conditions have been checked; if triggered, incident response has been invoked.
- [ ] The session log is updated with completed, in-progress, discovered, and reprioritized items.

## 9. Confidence Model Reminders

Tag every major claim:

- `[FACT]` — Directly observed divergence, commit diff, command output, or test result.
- `[INFERENCE]` — Reasonable deduction from direct evidence.
- `[HYPOTHESIS]` — A plausible breaking change that still needs bisect or test confirmation.
- `[NEEDS_VERIFICATION]` — Not yet proven; must not be presented as the confirmed regression cause.

Never claim a regression is fixed until the end-to-end regression test passes on the fixed commit.
