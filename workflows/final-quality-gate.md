# Final Quality Gate & Pre-Delivery Audit Workflow

This workflow guides the host AI agent through the final verification pass before publishing audit findings or applying remediations.

## 1. Objective

Enforce the definition of done (DoD), pre-delivery checklist, and automated quality gates defined in [`references/pre-delivery-gates.md`](../references/pre-delivery-gates.md) and [`references/quality-gates.md`](../references/quality-gates.md).

## 2. Prerequisites

Before running the final quality gate, confirm the following:

- [ ] All analysis and artifact-generation workflows are complete.
- [ ] `HQE_FINDINGS.json`, `HQE_RUN_MANIFEST.json`, and `HQE_SESSION_LOG.json` exist and are schema-valid.
- [ ] `scripts/validate_findings.py`, `scripts/validate_semantics.py`, `scripts/validate_manifest.py`, and `scripts/validate_session_log.py` are runnable.
- [ ] `references/pre-delivery-gates.md` and `references/quality-gates.md` are available for reference.
- [ ] A clean diff or baseline is available for remediation runs.

## 3. Entry Criteria

Begin this workflow when any of the following are true:

- Artifacts have been generated and are ready for delivery.
- A remediation run is complete and ready for sign-off.
- The user explicitly requests a final quality check.
- Any workflow transitions to the pre-delivery phase.

## 4. Stop-the-Line Conditions

Immediately halt and invoke [`workflows/incident-response.md`](incident-response.md) if any of the following are found during the quality gate:

- Unredacted credentials, API keys, tokens, or private keys in any artifact.
- Evidence of a backdoor, malicious payload, or active exploitation discovered late.
- A CRITICAL finding cannot be verified and the repository is in production.
- Schema validation fails and cannot be resolved.

Flag the issue as `STOP-THE-LINE: [issue]` and resolve before delivery.

## 5. Execution Model

### Phase 1: Evidentiary Proof

**Goal**: Confirm every finding is substantiated by evidence.

1. **Verify path and line integrity**:
   - Every finding has a `path` that exists in the repository.
   - Line ranges are valid (`start_line >= 1`, `end_line >= start_line`).
   - Anchors include a `grep_signature` when lines are unavailable.
2. **Verify snippet quality**:
   - Snippets are 2–5 lines.
   - Snippets include the sink and, if nearby, the validation/auth gate.
   - Snippets match the file on disk.
3. **Verify zero hallucination**:
   - No placeholder paths such as `path/to/file`.
   - No invented line numbers or function names.

**Evidence to collect**:
- Evidence triad checklist per finding.
- List of findings failing evidentiary proof and remediation actions.

**Exit criteria**:
- [ ] Every finding has valid line bounds or anchor+grep.
- [ ] Every snippet is non-empty and relevant.

### Phase 2: Severity & Taint Chain Integrity

**Goal**: Confirm severity and security metadata meet protocol requirements.

1. **Check severity gates** for all `CRITICAL` and `HIGH` findings:
   - `preconditions`
   - `exploitability`
   - `blast_radius`
   - `likelihood` and `likelihood_justification`
   - `exposure_evidence`
2. **Check taint chains** for all `SEC` findings:
   - `source`
   - `transforms`
   - `validation_boundary`
   - `sink`
   - `impact`
3. **Downgrade or tag** findings that lack required fields as `[NEEDS_VERIFICATION]`.

**Evidence to collect**:
- Severity-gate checklist.
- Taint-chain checklist for security findings.
- Downgrade/retag decisions.

**Exit criteria**:
- [ ] All `CRITICAL` and `HIGH` findings satisfy severity gates.
- [ ] All `SEC` findings have complete taint chains.

### Phase 3: Change Budget & Anti-Regression (Remediation Runs)

**Goal**: Ensure remediation changes are safe and well-scoped.

1. **Verify modified file count** is ≤ 5 per TODO-ID.
2. **Flag any behavioral or dependency change** explicitly:
   - `[BEHAVIOR CHANGE]` for observable behavior changes.
   - `[NEW_DEPENDENCY]` for added packages/tools.
3. **Confirm rollback steps** are documented for high-risk changes.
4. **Run Tier 1 verification tests** and confirm they pass.

**Evidence to collect**:
- Modified file list.
- Behavior-change and new-dependency flags.
- Test command outputs.

**Exit criteria**:
- [ ] Modified file count is within budget or explicitly justified.
- [ ] All behavior/dependency changes are flagged.
- [ ] Tier 1 verification tests pass (or failures are documented and accepted).

### Phase 4: Artifact Completeness

**Goal**: Confirm all required artifacts are present and valid.

1. **Run schema validation** on all machine-readable artifacts:
   ```bash
   python3 scripts/validate_findings.py HQE_FINDINGS.json
   python3 scripts/validate_semantics.py HQE_FINDINGS.json
   python3 scripts/validate_manifest.py HQE_RUN_MANIFEST.json
   python3 scripts/validate_session_log.py HQE_SESSION_LOG.json
   ```
2. **Check artifact inventory** against the Exhaustive output profile:
   - `HQE_REPORT.md`
   - `HQE_FINDINGS.json`
   - `HQE_RUN_MANIFEST.json`
   - `HQE_RISK_REGISTER.md`
   - `HQE_MASTER_TODO.md`
   - `HQE_PATTERN_FINDINGS.md`
   - `HQE_QUICK_WINS_VS_STRUCTURAL.md`
   - `HQE_SECURITY_POSTURE.md`
   - `HQE_RELIABILITY.md`
   - `HQE_TESTING_GAPS.md`
   - `HQE_UNKNOWNS.md`
   - `HQE_CONFIDENCE.md`
   - `HQE_SESSION_LOG.json`
3. **Cross-check counts and IDs** across artifacts.

**Evidence to collect**:
- Validation command outputs.
- Artifact inventory checklist.
- Consistency check results.

**Exit criteria**:
- [ ] All machine-readable artifacts pass schema validation.
- [ ] All required Markdown artifacts are present and non-empty.
- [ ] IDs and counts are consistent across artifacts.

### Phase 5: Self-Review

**Goal**: Catch omissions, inconsistencies, and quality gaps before delivery.

1. **Re-read the executive summary** for accuracy against findings.
2. **Check for vague recommendations**; every remediation must specify WHERE and WHAT.
3. **Check for assumptions presented as facts**.
4. **Verify style-only findings** have been filtered unless they mask bugs, affect security/reliability, or measurably degrade maintainability.
5. **Confirm reproducibility manifest** notes tooling, commands attempted, and limitations.

**Evidence to collect**:
- Self-review checklist.
- List of issues caught and fixed.

**Exit criteria**:
- [ ] Self-review is complete.
- [ ] All caught issues are resolved or documented as blockers.

## 6. Required Controls / Checks

- Every finding must have valid line bounds and a non-empty code snippet.
- Snippets must be sanitized with zero unredacted secrets.
- All `CRITICAL` and `HIGH` findings must satisfy severity gates.
- All `SEC` findings must have complete source-to-sink taint chains.
- Modified file count must be ≤ 5 per TODO-ID for remediation runs.
- Any behavioral or dependency change must be flagged with `[BEHAVIOR CHANGE]` or `[NEW_DEPENDENCY]`.
- Tier 1 verification tests must run and pass for remediation runs.
- Run manifests, session logs, and audit deliverables must pass schema validation.
- Output caps must be respected.
- Style-only findings must be filtered unless they meet the exception criteria.

## 7. Artifact Outputs

- Updated `HQE_FINDINGS.json` (with any gate-required downgrades or retags).
- Updated `HQE_RUN_MANIFEST.json`.
- Updated `HQE_SESSION_LOG.json`.
- `HQE_QUALITY_GATE_REPORT.md` or equivalent notes (optional, may be appended to `HQE_CONFIDENCE.md`).
- `HQE_HANDOFF.md` (when remediation is requested; see [`workflows/handoff-generation.md`](handoff-generation.md)).

Validate machine-readable artifacts with:

```bash
python3 scripts/validate_findings.py HQE_FINDINGS.json
python3 scripts/validate_semantics.py HQE_FINDINGS.json
python3 scripts/validate_manifest.py HQE_RUN_MANIFEST.json
python3 scripts/validate_session_log.py HQE_SESSION_LOG.json
python3 scripts/validate_protocol_bundle.py
```

## 8. Exit Criteria

The final quality gate is complete when:

- [ ] Every finding passes evidentiary proof.
- [ ] All `CRITICAL`/`HIGH` findings satisfy severity gates.
- [ ] All `SEC` findings have complete taint chains.
- [ ] No unredacted secrets appear in any artifact.
- [ ] Remediation runs respect the change budget and behavior-change flags.
- [ ] All machine-readable artifacts pass schema validation.
- [ ] All required Markdown artifacts are present and internally consistent.
- [ ] Self-review is complete.
- [ ] Stop-the-line conditions have been checked and handled if triggered.
- [ ] The session log is updated with quality-gate completion.

## 9. Confidence Model Reminders

Tag quality-gate conclusions:

- `[FACT]` — Validation command passed, line bounds verified, secret scan clean.
- `[INFERENCE]` — Artifact consistency inferred from matching counts and IDs.
- `[HYPOTHESIS]` — A potential issue suspected but not yet reproduced.
- `[NEEDS_VERIFICATION]` — A gate item that could not be fully checked.

Never claim a quality gate passed unless every checked item has evidence. If a gate item cannot be verified, document it as a blocker or limitation rather than silently signing off.
