# Remediation Run Workflow

The `remediate` workflow (`/HQE remediate`) executes root-cause fixes for known findings while respecting the minimal-change bias, change budget, and anti-regression rules in `protocol/hqe-engineer.yaml`.

## 1. Objective

Apply safe, minimal fixes to confirmed findings, verify each fix independently, and produce a transparent record of what was fixed, what failed, and what remains open.

## 2. Prerequisites

Before starting remediation, confirm the following:

- [ ] Findings are confirmed or clearly marked with confidence tags.
- [ ] An HQE Handoff document or `HQE_FINDINGS.json` is available if remediation was handed off.
- [ ] The repository builds and tests run before changes begin.
- [ ] `git status` is clean or unrelated changes are protected.
- [ ] `protocol/hqe-engineer.yaml`, `references/remediation.md`, `references/change-control.md`, and `references/patch-packaging.md` are available for reference.
- [ ] Schema validators in `scripts/` are runnable (`python3 scripts/validate_findings.py`, etc.).

## 3. Entry Criteria

Begin this workflow when any of the following are true:

- User invokes `/HQE remediate` with a finding list or handoff.
- A previous audit produced confirmed findings and the user wants them fixed.
- A stop-the-line incident has been contained and the root cause is ready for safe removal.
- A handoff from `workflows/targeted-bug-hunt.md`, `workflows/debug-error.md`, or `workflows/trace-regression.md` requests remediation.

## 4. Stop-the-Line Conditions

Immediately halt remediation and invoke [`workflows/incident-response.md`](incident-response.md) if any of the following are found:

- Active credentials, API keys, tokens, or private keys exposed in the remediation scope.
- A backdoor, malicious payload, or remote-code-execution path in the remediation scope.
- A proposed fix would intentionally remove or alter behavior without explicit `[BEHAVIOR CHANGE]` approval.
- Evidence of active exploitation or unauthorized workflow modifications.

Flag the triggering item as `STOP-THE-LINE: [issue]` in the session log and do not proceed with normal remediation until incident response is complete.

## 5. Execution Model

### Phase 0: Ingest Handoff & Re-verify Context

**Goal**: Ensure the findings still apply to the current code state.

1. **Ingest handoff**:
   - If provided an HQE Handoff document (`HQE_HANDOFF.md`), read it carefully.
   - Load `HQE_FINDINGS.json` and the session log if available.
2. **Re-verify context**:
   - Ensure the findings still apply to the current code state.
   - Re-read the affected files and confirm the evidence locations are unchanged.
3. **Establish baseline**:
   - Run the relevant tests or build commands to record pre-fix health.

**Evidence to collect**:
- Handoff summary and finding inventory.
- Baseline test/build results.
- Confirmation that evidence locations are still valid.

**Exit criteria**:
- [ ] Findings are loaded and confirmed against current code.
- [ ] Baseline health is recorded.

### Phase 1: Plan Minimal Fixes

**Goal**: Develop the smallest coherent fix for each finding.

1. **Plan per finding**:
   - Develop the smallest coherent fix that addresses the root cause.
   - Avoid speculative mass refactors during bug fixing.
2. **Respect change budget**:
   - Limit to `<= 5` files per finding/TODO-ID unless explicitly justified.
3. **Identify behavior changes**:
   - Flag any fix that removes or alters observable behavior with `[BEHAVIOR CHANGE]`.
   - Require explicit user approval before implementing behavior changes.
4. **Assess regression risk**:
   - Assign `Low`, `Medium`, or `High` regression risk per fix.
   - High-risk changes require rollback steps.

**Evidence to collect**:
- Fix plan per finding with files to change.
- Behavior-change flags and justifications.
- Regression risk and rollback notes.

**Exit criteria**:
- [ ] Each finding has a minimal fix plan.
- [ ] Behavior changes are flagged and approved or deferred.

### Phase 2: Iterative Execution

**Goal**: Apply fixes one finding at a time and validate before proceeding.

1. **Protect unrelated code**:
   - Check `git status` before editing.
   - Ensure you do not overwrite unrelated working-tree changes.
2. **Apply fix for Finding 1**:
   - Implement the minimal safe change.
   - Add or update tests for regression coverage.
3. **Run relevant validation tests**:
   - Run targeted tests for the modified behavior.
   - Run module tests and, if safe, broader tests.
4. **Proceed to Finding 2** only after Finding 1 is verified.
5. **Document outcomes**:
   - Record which findings were successfully fixed and verified, and which failed.

**Evidence to collect**:
- Diff per finding.
- Test results after each fix.
- Updated finding status (`FIXED`, `FIX_IN_PROGRESS`, `OPEN`).

**Exit criteria**:
- [ ] Each fix is applied and validated before the next begins.
- [ ] Failed validations are recorded with failure evidence.

### Phase 3: Regression & Static Validation

**Goal**: Ensure the cumulative changes do not break the project.

1. **Run the full relevant test suite**.
2. **Run static checks**: lint, typecheck, and any available static analysis.
3. **Run build** to ensure compilation/packaging still succeeds.
4. **Inspect the final diff** for drive-by cleanup or unintended changes.

**Evidence to collect**:
- Full test suite results.
- Lint/typecheck/build results.
- Final diff review notes.

**Exit criteria**:
- [ ] Full relevant test suite passes or failures are documented and accepted.
- [ ] Static checks and build pass.
- [ ] No drive-by cleanup remains in the diff.

### Phase 4: Consolidation & Artifact Generation

**Goal**: Produce clean, consistent deliverables.

1. **Update finding statuses**:
   - Update the status of each finding (`FIXED`, `REOPENED`, `DEFERRED`, etc.).
2. **Emit remediation artifacts**:
   - `HQE_REPORT.md` remediation section.
   - Updated `HQE_FINDINGS.json`.
   - `HQE_RUN_MANIFEST.json`.
   - `HQE_SESSION_LOG.json`.
3. **Validate** all JSON artifacts against schemas in `schemas/`.

**Evidence to collect**:
- Final artifact set.
- Schema-validation output.
- Updated session log.

**Exit criteria**:
- [ ] All deliverables written and pre-delivery gates satisfied.
- [ ] Schema validation passes.

## 6. Required Controls / Checks

- Re-verify every finding against current code before fixing it.
- Limit each finding/TODO-ID to `<= 5` changed files unless explicitly justified.
- Do not perform speculative mass refactors during remediation.
- Every fix must include verification commands and expected results.
- Add or update regression tests for each behavior-affecting fix.
- Flag `[BEHAVIOR CHANGE]` and require explicit approval before implementation.
- High-risk changes require rollback steps.
- Run tests honestly; never report a test as passing unless it was executed.
- Protect unrelated working-tree changes; check `git status` before editing.
- Update finding statuses in `HQE_FINDINGS.json` accurately.

## 7. Artifact Outputs

- `HQE_REPORT.md` (remediation summary and outcomes)
- `HQE_FINDINGS.json` (updated statuses)
- `HQE_RUN_MANIFEST.json`
- `HQE_SESSION_LOG.json`
- `HQE_HANDOFF.md` (if further work is handed off)

Validate machine-readable artifacts with:

```bash
python3 scripts/validate_findings.py HQE_FINDINGS.json
python3 scripts/validate_manifest.py HQE_RUN_MANIFEST.json
python3 scripts/validate_session_log.py HQE_SESSION_LOG.json
```

## 8. Exit Criteria

Remediation is complete when:

- [ ] All phases above have been executed or explicitly skipped with justification.
- [ ] Each finding is fixed, deferred, or explicitly remains open with a blocker.
- [ ] Every fix is verified with a Tier 1, 2, or 3 validation.
- [ ] Full relevant test suite passes or failures are documented and accepted.
- [ ] No drive-by cleanup or unintended changes remain.
- [ ] Artifacts are emitted and schema-validated.
- [ ] Stop-the-line conditions have been checked; if triggered, incident response has been invoked.
- [ ] The session log is updated with completed, in-progress, discovered, and reprioritized items.

## 9. Confidence Model Reminders

Tag every major claim:

- `[FACT]` — Directly verified fix, test result, or command output.
- `[INFERENCE]` — Reasonable deduction from direct evidence.
- `[HYPOTHESIS]` — A plausible but unverified explanation for a failed validation.
- `[NEEDS_VERIFICATION]` — A fix that could not be verified in the current environment.

Never claim a finding is fixed until its verification command passes.
