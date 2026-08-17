# Evidence Capture & Triad Validation Workflow

This workflow guides the host AI agent through collecting, validating, and recording evidence triads for every candidate finding.

## 1. Objective

Ensure 100% evidentiary compliance: zero unsubstantiated claims, verified file paths, non-empty code snippets, automated secret redaction, and reproducible command records.

## 2. Prerequisites

Before capturing evidence, confirm the following:

- [ ] The `runtime.EvidenceStore` class is importable.
- [ ] `scripts/redact_secrets.py` is available and runnable.
- [ ] The finding schema (`schemas/finding.schema.json`) is understood.
- [ ] The repository files are accessible on disk (not truncated or read-only unless noted).

## 3. Entry Criteria

Begin this workflow whenever any of the following occur:

- A candidate finding is identified during any analysis phase.
- A command execution result needs to be recorded for verification.
- A snippet, log, or stack trace is being added to a finding.
- A finding is being upgraded from `[HYPOTHESIS]` to `[INFERENCE]` or `[FACT]`.

## 4. Stop-the-Line Conditions

Immediately halt and invoke [`workflows/incident-response.md`](incident-response.md) if any of the following are found during evidence capture:

- Raw credentials, API keys, tokens, or private keys are discovered and cannot be redacted.
- Evidence points to a backdoor, malicious payload, or active exploitation.
- A finding's evidence references a file that does not exist and no anchor can be located.

Flag the issue as `STOP-THE-LINE: [issue]` and do not finalize the finding until resolved.

## 5. Execution Model

### Phase 0: Capture Source Snippet

**Goal**: Read and record the exact source evidence from disk.

1. **Locate the target**:
   - Prefer exact `file:line` ranges.
   - If lines are unavailable, use a structural anchor (`symbol`, `anchor`, `grep_signature`) per `protocol/hqe-engineer.yaml` constraint C2.
2. **Read the suspect code chunk** from disk:
   ```python
   from runtime import EvidenceStore
   store = EvidenceStore(repo_root=".")
   ev = store.add_evidence(
       path="src/auth.rs",
       start_line=52,
       end_line=56,
       snippet="let secret = std::env::var(\"JWT_SECRET\").unwrap_or_else(...);",
       verify_against_disk=True
   )
   ```
3. **Verify snippet relevance**:
   - The snippet MUST include the sink (dangerous operation) and, if nearby, the validation/auth gate.
   - Do not quote unrelated adjacent lines to satisfy length.

**Evidence to collect**:
- Exact relative file path from repository root.
- Line range (`start_line >= 1`, `end_line >= start_line`) or anchor + grep signature.
- Verbatim 2–5 line snippet matching the file on disk.

**Exit criteria**:
- [ ] Evidence triad (path, line/anchor, snippet) is complete.
- [ ] Snippet has been verified against disk or marked `[NEEDS_VERIFICATION]`.

### Phase 1: Triad Validation

**Goal**: Confirm the evidence is locatable and internally consistent.

1. **Validate path**: file exists under the repository root.
2. **Validate line bounds**: `start_line` and `end_line` are within the file and `end_line >= start_line`.
3. **Validate snippet presence**: the snippet text appears in the indicated range or anchor location.
4. **Validate grep signature**: if using an anchor, provide a precise `grep` string that reproduces the snippet.
5. **Reject placeholder evidence**: no `TODO`, `FIXME`, `path/to/file`, or invented line numbers.

**Evidence to collect**:
- Validation result (pass/fail) for each triad component.
- Corrected evidence if the first attempt failed validation.

**Exit criteria**:
- [ ] Path, line bounds, and snippet are internally consistent.
- [ ] Anchor + grep signature is provided when lines are unavailable.

### Phase 2: Secret Redaction Pass

**Goal**: Ensure no raw credentials or sensitive values leak into findings or artifacts.

1. **Run all captured snippets through `scripts/redact_secrets.py`** regex filters.
2. **Redact any discovered secret** using deterministic placeholders such as `REDACTED_AWS_ACCESS_KEY_1` or the `ABCD…WXYZ` first-4/last-4 format.
3. **Verify redaction** by re-reading the evidence payload before attaching it to a finding.
4. **Do not reproduce full secrets** even when citing file:line or anchor+grep for location.

**Evidence to collect**:
- Redacted snippet.
- Redaction log entry (if applicable) noting what type of secret was redacted and where.

**Exit criteria**:
- [ ] No raw credentials, tokens, or private keys appear in final payloads.
- [ ] Redaction has been verified by a second pass.

### Phase 3: Record Command Executions

**Goal**: Make verification reproducible by capturing commands and their outcomes.

1. When a test or verification command is executed, capture:
   - Tool name.
   - Exact command string.
   - Exit code.
   - Relevant stdout/stderr excerpts (redacted if needed).
2. Use the evidence store:
   ```python
   store.record_tool_execution(
       tool_name="cargo_test",
       command="cargo test test_auth",
       exit_code=0,
       stdout="test test_auth ... ok"
   )
   ```
3. For failing commands, record the failure mode and any diagnostic next steps.

**Evidence to collect**:
- Command string, exit code, and sanitized output.
- Tier 1/2/3 verification classification per `protocol/hqe-engineer.yaml`.

**Exit criteria**:
- [ ] Every verification command is recorded with exit code and output.
- [ ] Outputs are sanitized of secrets.

### Phase 4: Attach Evidence to Finding

**Goal**: Integrate validated evidence into the canonical finding record.

1. Add the evidence object to the finding's `evidence` array.
2. Set the finding's `confidence` tag based on evidence strength:
   - `[FACT]` for directly verified evidence.
   - `[INFERENCE]` for strongly supported conclusions.
   - `[HYPOTHESIS]` for suspected but unverified claims.
   - `[NEEDS_VERIFICATION]` when evidence is incomplete.
3. Ensure the finding's `status` reflects the evidence state (`CONFIRMED`, `STRONGLY_SUPPORTED`, `SUSPECTED`, etc.).
4. Validate the resulting finding against `schemas/finding.schema.json`.

**Evidence to collect**:
- Final finding JSON with evidence array.
- Schema-validation result.

**Exit criteria**:
- [ ] Evidence is attached and the finding is schema-valid.
- [ ] Confidence tag accurately reflects evidence strength.

## 6. Required Controls / Checks

- Every finding MUST include at least one valid evidence triad:
  1. Exact relative file path.
  2. Line range (`start_line >= 1`, `end_line >= start_line`) OR structural anchor (`symbol`/`anchor` + `grep_signature`).
  3. Verifiable 2–5 line verbatim code snippet.
- Snippet relevance rule: the snippet MUST include the sink and, if nearby, the validation/auth gate.
- Never invent or approximate line numbers.
- Never output raw credentials, API keys, tokens, private keys, or PII.
- Record command executions with exact commands, exit codes, and sanitized outputs.
- Validate every finding against `schemas/finding.schema.json` before accepting it.

## 7. Artifact Outputs

- Evidence entries inside `HQE_FINDINGS.json`.
- Updated `HQE_SESSION_LOG.json` with evidence-capture progress.
- `HQE_REDACTION_LOG.md` (when secrets are redacted).
- Verification command records inside findings or session log.

Validate machine-readable artifacts with:

```bash
python3 scripts/validate_findings.py HQE_FINDINGS.json
python3 scripts/validate_session_log.py HQE_SESSION_LOG.json
```

## 8. Exit Criteria

Evidence capture is complete for a finding when:

- [ ] A valid evidence triad is present and verified.
- [ ] The snippet is relevant (includes sink and nearby validation/auth gate).
- [ ] Secrets are redacted and verified.
- [ ] The finding is schema-valid.
- [ ] Confidence tag reflects evidence strength.
- [ ] Verification commands (if any) are recorded with exit codes and sanitized outputs.
- [ ] Stop-the-line conditions have been checked and handled if triggered.

## 9. Confidence Model Reminders

Tag every finding based on its evidence:

- `[FACT]` — Directly verified with `file:line` + snippet from disk.
- `[INFERENCE]` — Derived from evidence but requires one deductive step.
- `[HYPOTHESIS]` — Suspected; include steps to confirm or refute.
- `[NEEDS_VERIFICATION]` — Incomplete evidence; must not be reported as a confirmed finding.

Never upgrade confidence without new evidence. If a taint-chain step or line location cannot be proven, keep the finding at `[NEEDS_VERIFICATION]` or downgrade it.
