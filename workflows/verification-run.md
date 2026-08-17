# Verification Run Workflow

The `verify` workflow (`/HQE verify`) rigorously proves or disproves that a fix resolves the original finding and that no regressions were introduced. It is governed by `protocol/hqe-engineer.yaml` verification_realism tiers and the verification_honesty_policy.

## 1. Objective

Confirm that remediations, claims, or reported fixes actually resolve the targeted issue without breaking adjacent behavior. Produce a transparent verification report with executed commands, observed outputs, and confidence tags.

## 2. Prerequisites

Before starting verification, confirm the following:

- [ ] The original finding or claim is documented with evidence and reproduction steps.
- [ ] The purported fix is applied (commit, diff, or branch).
- [ ] The repository builds and the relevant test commands are known.
- [ ] `protocol/hqe-engineer.yaml` and `references/verification.md` are available for reference.
- [ ] Schema validators in `scripts/` are runnable (`python3 scripts/validate_findings.py`, etc.).

## 3. Entry Criteria

Begin this workflow when any of the following are true:

- User invokes `/HQE verify <finding or claim>`.
- A remediation run has completed and needs independent verification.
- A PR or patch claims to fix an issue and the user wants proof.
- A finding was previously marked `FIX_IN_PROGRESS` and now needs validation.

## 4. Stop-the-Line Conditions

Immediately halt verification and invoke [`workflows/incident-response.md`](incident-response.md) if any of the following are found:

- Active credentials, API keys, tokens, or private keys exposed in verification outputs.
- A backdoor, malicious payload, or remote-code-execution path introduced by the purported fix.
- Verification reveals a critical data-loss or data-corruption path.
- Evidence of active exploitation or unauthorized workflow modifications.

Flag the triggering item as `STOP-THE-LINE: [issue]` in the session log and do not proceed with normal verification until incident response is complete.

## 5. Execution Model

### Phase 0: Ingest Claim & Establish Baseline

**Goal**: Understand what is being verified and record the starting state.

1. **Ingest claim**:
   - Read the original finding, handoff, or patch description.
   - Identify the exact behavior that the fix is supposed to change or preserve.
2. **Check out the fixed state**:
   - Ensure the purported fix is present in the working tree or target branch/commit.
3. **Establish baseline**:
   - Run the relevant tests or build commands to record pre-verification health.

**Evidence to collect**:
- Original finding or claim with evidence references.
- Fixed state location (commit, branch, files changed).
- Baseline test/build results.

**Exit criteria**:
- [ ] Claim and expected outcome are documented.
- [ ] Fixed state is present and baseline health is recorded.

### Phase 1: Reproduce Original Finding

**Goal**: Confirm the original issue is present in the unfixed state and that the reproduction is valid.

1. **Re-run the reproduction steps** from the original finding on the pre-fix state if possible.
2. **Record the observed failure** with exact command, output, and exit code.
3. **If the original issue cannot be reproduced**, document why (environment, missing inputs, already fixed).

**Evidence to collect**:
- Reproduction command and output on pre-fix state.
- Confirmation that the reproduction is valid.

**Exit criteria**:
- [ ] Original issue is reproduced or its irreproducibility is documented.

### Phase 2: Tiered Verification

**Goal**: Apply the strongest feasible verification tier for each claim.

1. **Tier 1 — Existing repo command**:
   - Use package scripts, CI commands, Makefile targets, or project test commands.
   - Record exact command and observed output.
2. **Tier 2 — New reproduction test**:
   - If no existing command covers the fix, write a minimal test stub.
   - Mark it `TO ADD` if it cannot be committed in this run.
3. **Tier 3 — Static / manual checklist**:
   - When execution is unavailable, provide a static proof or manual checklist.
4. **Run verification**:
   - Execute the chosen verification for each finding.
   - Record actual outputs, not assumed results.

**Evidence to collect**:
- Verification tier per finding.
- Exact commands and observed outputs.
- Tier 2 test stubs if applicable.
- Tier 3 static proof or checklist.

**Exit criteria**:
- [ ] Each finding has a verified Tier 1, 2, or 3 result.
- [ ] Actual outputs are recorded, not assumptions.

### Phase 3: Regression Checks

**Goal**: Ensure the fix did not break existing behavior.

1. **Run targeted tests** for the affected area.
2. **Run module tests** for the affected package or module.
3. **Run the broader test suite** if safe and practical.
4. **Run static checks**: lint, typecheck, and any available static analysis.
5. **Run build** to ensure compilation/packaging still succeeds.

**Evidence to collect**:
- Test results at each scope.
- Lint/typecheck/build results.
- Any new failures with failure evidence.

**Exit criteria**:
- [ ] Regression checks pass or failures are documented and accepted.

### Phase 4: Report Verification Outcome

**Goal**: Produce a transparent verdict for each claim.

1. **Classify each finding**:
   - `VERIFIED` — verification passed and original issue is resolved.
   - `NOT_VERIFIED` — verification failed or could not be run; issue remains open.
   - `NEEDS_VERIFICATION` — insufficient evidence; exact follow-up steps provided.
2. **Document failed verifications**:
   - Include exact command, expected result, observed result, and likely failure modes.
3. **Update finding statuses** in `HQE_FINDINGS.json`.

**Evidence to collect**:
- Verdict per finding.
- Failure analysis for any `NOT_VERIFIED` items.
- Updated `HQE_FINDINGS.json`.

**Exit criteria**:
- [ ] Each finding has a clear verdict.
- [ ] Failed verifications include actionable follow-up steps.

### Phase 5: Consolidation & Artifact Generation

**Goal**: Produce clean, consistent deliverables.

1. **Emit verification artifacts**:
   - `HQE_REPORT.md` verification section.
   - `HQE_FINDINGS.json` with updated statuses.
   - `HQE_RUN_MANIFEST.json`.
   - `HQE_SESSION_LOG.json`.
2. **Validate** all JSON artifacts against schemas in `schemas/`.

**Evidence to collect**:
- Final artifact set.
- Schema-validation output.
- Updated session log.

**Exit criteria**:
- [ ] All deliverables written and pre-delivery gates satisfied.
- [ ] Schema validation passes.

## 6. Required Controls / Checks

- Never claim a fix works unless the verification command was actually executed.
- Always specify verification tier (Tier 1/2/3) and expected result.
- Include fallbacks where the strongest tier is unavailable.
- Run tests honestly; failed verifications must be reported, not silently downgraded.
- If verification cannot be run locally, tag as `[NEEDS_VERIFICATION]` and provide exact user-run steps.
- Do not declare success from compilation alone when behavior is involved.
- Update finding statuses accurately in `HQE_FINDINGS.json`.
- Use language like "This change **should** fix X; verify by running Y" when verification is pending.

## 7. Artifact Outputs

- `HQE_REPORT.md` (verification summary and verdicts)
- `HQE_FINDINGS.json` (updated statuses)
- `HQE_RUN_MANIFEST.json`
- `HQE_SESSION_LOG.json`
- `HQE_VALIDATION_REPORT.md` (detailed per-finding verification evidence)

Validate machine-readable artifacts with:

```bash
python3 scripts/validate_findings.py HQE_FINDINGS.json
python3 scripts/validate_manifest.py HQE_RUN_MANIFEST.json
python3 scripts/validate_session_log.py HQE_SESSION_LOG.json
```

## 8. Exit Criteria

Verification is complete when:

- [ ] All phases above have been executed or explicitly skipped with justification.
- [ ] Each finding has a clear verdict (`VERIFIED`, `NOT_VERIFIED`, or `NEEDS_VERIFICATION`).
- [ ] Verification commands and observed outputs are recorded for each meaningful claim.
- [ ] Regression checks pass or failures are documented and accepted.
- [ ] Artifacts are emitted and schema-validated.
- [ ] Stop-the-line conditions have been checked; if triggered, incident response has been invoked.
- [ ] The session log is updated with completed, in-progress, discovered, and reprioritized items.

## 9. Confidence Model Reminders

Tag every major claim:

- `[FACT]` — Verification command was executed and produced the observed output.
- `[INFERENCE]` — Strong deduction from verification results.
- `[HYPOTHESIS]` — A plausible explanation for an unexpected verification result.
- `[NEEDS_VERIFICATION]` — Verification could not be executed; exact steps provided.

Never claim a finding is `VERIFIED` unless the verification command actually passed in the environment.
