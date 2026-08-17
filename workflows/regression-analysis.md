# Regression Analysis Workflow

The `regression` workflow (`/HQE regression`) investigates newly discovered regressions, determines their root cause, and decides whether the change was intentional or a defect. It is closely related to `workflows/trace-regression.md` but focuses on analysis and triage rather than deep multi-hop tracing.

## 1. Objective

Determine whether an observed behavior change is a regression, identify the root cause and responsible change set, classify severity, and produce either a remediation plan or a documented `[BEHAVIOR CHANGE]` justification.

## 2. Prerequisites

Before starting regression analysis, confirm the following:

- [ ] The observed behavior change and the expected prior behavior are documented.
- [ ] Git history is available for the affected paths.
- [ ] A reproduction command or test case exists (or can be constructed) that demonstrates the change.
- [ ] `protocol/hqe-engineer.yaml` and `references/reasoning-methodologies.md` are available for reference.
- [ ] Schema validators in `scripts/` are runnable (`python3 scripts/validate_findings.py`, etc.).

## 3. Entry Criteria

Begin this workflow when any of the following are true:

- User invokes `/HQE regression <symptom>`.
- A test, user report, or monitoring alert indicates behavior changed unexpectedly.
- A release candidate differs from the previous release in a way that may not be intended.
- A PR or commit is suspected of causing downstream breakage.

## 4. Stop-the-Line Conditions

Immediately halt regression analysis and invoke [`workflows/incident-response.md`](incident-response.md) if any of the following are found:

- Active credentials, API keys, tokens, or private keys exposed in the regression range.
- A backdoor, malicious payload, or remote-code-execution path introduced by the suspected regression.
- A critical data-loss or data-corruption path reachable from the changed behavior.
- Evidence of active exploitation or unauthorized workflow modifications.

Flag the triggering item as `STOP-THE-LINE: [issue]` in the session log and do not proceed with normal artifact generation until incident response is complete.

## 5. Execution Model

### Phase 0: Symptom Capture & Baseline

**Goal**: Document the observed change and establish a known-good baseline.

1. **Capture the symptom**:
   - Record exact observed behavior, output, error, or state change.
   - Include environment, version, and reproduction frequency.
2. **Define expected behavior**:
   - Document what the system did previously or what the contract requires.
3. **Establish baseline**:
   - Identify the last known-good commit, release, or test run.
   - Record the baseline result for comparison.

**Evidence to collect**:
- Symptom description with exact output or state.
- Expected behavior statement.
- Baseline commit and result.

**Exit criteria**:
- [ ] Symptom and expected behavior are documented.
- [ ] Known-good baseline is identified.

### Phase 1: Scope & Change Identification

**Goal**: Identify the change set most likely responsible for the regression.

1. **List candidate changes**:
   - Use `git log --oneline -- <affected paths>` to find recent commits.
   - Include merged PRs, dependency updates, and configuration changes.
2. **Inspect diffs**:
   - Review diff hunks for behavior-affecting changes.
   - Look for altered defaults, changed signatures, modified validation, or removed checks.
3. **Check related issues/PRs**:
   - Read PR descriptions, commit messages, and issue comments for intent.

**Evidence to collect**:
- Candidate commits/PRs with authors and dates.
- Diff hunk analysis.
- Intent documentation (PR description, commit message).

**Exit criteria**:
- [ ] Candidate change set is identified.
- [ ] Intent of each candidate is understood.

### Phase 2: Root-Cause Determination

**Goal**: Decide whether the change is a regression or an intentional behavior change.

1. **Reproduce on the suspected commit**:
   - Confirm the symptom appears after the suspected change and not before.
2. **Apply CAGEERF or 5W1H**:
   - Trace genesis, evolution, and effect of the change.
3. **Classify the finding**:
   - `HQE-BUG-xxx` if the change violates documented or implied contract.
   - `HQE-REL-xxx` if it affects reliability, observability, or resilience.
   - Tag `[BEHAVIOR CHANGE]` if the change is intentional but user-visible.

**Evidence to collect**:
- Reproduction result on suspected commit.
- Root-cause analysis with `file:line` snippets.
- Classification and confidence tag.

**Exit criteria**:
- [ ] Root cause is identified with evidence.
- [ ] Change is classified as regression, intended behavior change, or inconclusive.

### Phase 3: Impact & Severity Assessment

**Goal**: Determine how the regression affects users, systems, and downstream code.

1. **Assess blast radius**:
   - Identify callers, consumers, tests, or deployments affected.
2. **Determine severity**:
   - Use `protocol/hqe-engineer.yaml` severity definitions.
   - CRITICAL/HIGH findings require severity-gate fields.
3. **Check for anti-regression violations**:
   - If the regression was caused by a previous fix that removed behavior, flag it per the anti-regression rule.

**Evidence to collect**:
- Blast radius list.
- Severity justification.
- Anti-regression flag if applicable.

**Exit criteria**:
- [ ] Blast radius and severity are documented.
- [ ] CRITICAL/HIGH findings satisfy severity-gate fields.

### Phase 4: Remediation or Behavior-Change Approval

**Goal**: Decide the path forward and document the plan.

1. **If regression**: follow [`workflows/remediation-run.md`](remediation-run.md) to restore expected behavior.
2. **If intentional behavior change**:
   - Document the `[BEHAVIOR CHANGE]` with old behavior, new behavior, reason, and migration impact.
   - Require explicit user approval before closing as intentional.
3. **If inconclusive**: provide exact follow-up steps and mark `[NEEDS_VERIFICATION]`.

**Evidence to collect**:
- Remediation plan or behavior-change documentation.
- Approval record or follow-up steps.

**Exit criteria**:
- [ ] Regression has a remediation plan, or behavior change is documented and approved, or follow-up steps are provided.

### Phase 5: Consolidation & Artifact Generation

**Goal**: Produce clean, consistent deliverables.

1. **Deduplicate findings** by root cause.
2. **Emit regression analysis artifacts**.
3. **Validate** all JSON artifacts against schemas in `schemas/`.
4. **Update the session log** with completed, in-progress, discovered, and reprioritized items.

**Evidence to collect**:
- Final artifact set.
- Schema-validation output.
- Updated session log.

**Exit criteria**:
- [ ] All deliverables written and pre-delivery gates satisfied.
- [ ] Schema validation passes.

## 6. Required Controls / Checks

- Every regression must cite both expected and observed behavior.
- The responsible change set must be anchored to commits, diffs, or `file:line`.
- Distinguish regressions from intentional behavior changes; do not assume all changes are bugs.
- Flag `[BEHAVIOR CHANGE]` and require explicit approval for intentional user-visible changes.
- CRITICAL/HIGH findings must satisfy severity-gate fields.
- Claims must cite exact file paths, line numbers, and 2–5 line snippets.
- Mark inconclusive causes as `[NEEDS_VERIFICATION]` with exact follow-up steps.
- Run tests honestly; never report a test as passing unless it was executed.

## 7. Artifact Outputs

- `HQE_REPORT.md` (regression analysis and disposition)
- `HQE_FINDINGS.json`
- `HQE_RUN_MANIFEST.json`
- `HQE_SESSION_LOG.json`
- `HQE_PATTERN_FINDINGS.md` (if the analysis reveals recurring anti-patterns)
- `HQE_HANDOFF.md` (when handing off remediation to another agent)

Validate machine-readable artifacts with:

```bash
python3 scripts/validate_findings.py HQE_FINDINGS.json
python3 scripts/validate_manifest.py HQE_RUN_MANIFEST.json
python3 scripts/validate_session_log.py HQE_SESSION_LOG.json
```

## 8. Exit Criteria

Regression analysis is complete when:

- [ ] All phases above have been executed or explicitly skipped with justification.
- [ ] The root cause is identified or explicitly marked `[NEEDS_VERIFICATION]`.
- [ ] The change is classified as regression, intended behavior change, or inconclusive.
- [ ] Severity and blast radius are documented.
- [ ] A remediation plan, behavior-change approval, or follow-up steps exist.
- [ ] Artifacts are emitted and schema-validated.
- [ ] Stop-the-line conditions have been checked; if triggered, incident response has been invoked.
- [ ] The session log is updated with completed, in-progress, discovered, and reprioritized items.

## 9. Confidence Model Reminders

Tag every major claim:

- `[FACT]` — Directly observed behavior change, commit diff, command output, or test result.
- `[INFERENCE]` — Reasonable deduction from direct evidence.
- `[HYPOTHESIS]` — A plausible responsible change that still needs bisect or test confirmation.
- `[NEEDS_VERIFICATION]` — Not yet proven; must not be presented as the confirmed root cause.

Never classify a change as intentional without evidence of explicit intent (commit message, PR description, approved design doc).
