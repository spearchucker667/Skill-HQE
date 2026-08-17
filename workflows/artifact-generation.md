# Artifact Generation & Assembly Workflow

This workflow guides the host AI agent through compiling findings and session metadata into the canonical HQE deliverables.

## 1. Objective

Deterministically assemble verified findings into machine-readable JSON and human-readable Markdown artifacts using the `runtime.artifact_pipeline` engine and the `scripts/build_artifacts.py` tooling.

## 2. Prerequisites

Before generating artifacts, confirm the following:

- [ ] `HQE_FINDINGS.json` exists and has passed schema and semantic validation.
- [ ] `HQE_SESSION_LOG.json` exists and is schema-valid.
- [ ] `scripts/build_artifacts.py`, `scripts/create_run_manifest.py`, and `scripts/validate_protocol_bundle.py` are present and runnable.
- [ ] `templates/` contains the required Markdown templates.
- [ ] Output caps from `protocol/hqe-engineer.yaml` are understood (30 CRITICAL/HIGH total, 25 MEDIUM, 20 LOW one-liners).

## 3. Entry Criteria

Begin this workflow when any of the following are true:

- All analysis phases are complete and findings have been consolidated and prioritized.
- The user explicitly requests artifact generation.
- A remediation or verification run has produced validated findings that need to be packaged.

## 4. Stop-the-Line Conditions

Immediately halt artifact generation and invoke [`workflows/incident-response.md`](incident-response.md) if any of the following are found:

- `HQE_FINDINGS.json` contains unredacted secrets or credentials.
- Schema validation fails and cannot be resolved.
- Findings contain invented file paths, line numbers, or anchors.
- A CRITICAL/HIGH finding is missing required severity-gate fields.

Flag the issue as `STOP-THE-LINE: [issue]` and resolve before emitting artifacts.

## 5. Execution Model

### Phase 1: Validate Findings Collection

**Goal**: Ensure the input data is clean before assembly.

1. **Validate JSON schema**:
   ```bash
   python3 scripts/validate_findings.py HQE_FINDINGS.json
   ```
2. **Validate semantic invariants** (severity gates, taint chains, line bounds):
   ```bash
   python3 scripts/validate_semantics.py HQE_FINDINGS.json
   ```
3. **Check for secret leakage** by running snippets through `scripts/redact_secrets.py`.
4. **Review validation output** and fix any blocking errors before proceeding.

**Evidence to collect**:
- Schema-validation output.
- Semantic-validation output.
- Secret-redaction check result.

**Exit criteria**:
- [ ] `HQE_FINDINGS.json` passes schema validation.
- [ ] Semantic invariants pass.
- [ ] No unredacted secrets remain.

### Phase 2: Assemble Canonical Deliverables

**Goal**: Generate the nine canonical Markdown artifacts.

1. **Run the artifact builder**:
   ```bash
   python3 scripts/build_artifacts.py HQE_FINDINGS.json --output-dir .
   ```
2. The pipeline deterministically generates:
   - `HQE_RISK_REGISTER.md`
   - `HQE_MASTER_TODO.md`
   - `HQE_PATTERN_FINDINGS.md`
   - `HQE_QUICK_WINS_VS_STRUCTURAL.md`
   - `HQE_SECURITY_POSTURE.md`
   - `HQE_RELIABILITY.md`
   - `HQE_TESTING_GAPS.md`
   - `HQE_UNKNOWNS.md`
   - `HQE_CONFIDENCE.md`
3. **Verify each artifact** is non-empty and internally consistent.

**Evidence to collect**:
- Build command output.
- Generated artifact file list.
- Any build warnings or errors.

**Exit criteria**:
- [ ] All nine canonical Markdown artifacts are generated.
- [ ] No build errors remain.

### Phase 3: Generate Report

**Goal**: Produce the top-level human-readable report.

1. **Generate `HQE_REPORT.md`** containing:
   - Executive summary with health score and top priorities.
   - Methodologies applied.
   - High-level findings by category.
   - Immediate actions and implementation roadmap.
2. Ensure the report references the canonical artifacts by stable finding IDs.

**Evidence to collect**:
- `HQE_REPORT.md` content.
- Cross-references to detailed artifacts.

**Exit criteria**:
- [ ] `HQE_REPORT.md` exists and is internally consistent with findings.

### Phase 4: Generate Run Manifest

**Goal**: Produce the machine-readable run manifest.

1. **Generate `HQE_RUN_MANIFEST.json`**:
   ```bash
   python3 scripts/create_run_manifest.py --findings-file HQE_FINDINGS.json --output HQE_RUN_MANIFEST.json
   ```
2. Ensure the manifest captures:
   - Run ID, protocol version, timestamp.
   - Repository identity and commit/branch.
   - Coverage mode and subsystem counts.
   - Health score with evidence-backed reasons.
   - Artifact inventory.
3. **Validate the generated manifest**:
   ```bash
   python3 scripts/validate_manifest.py HQE_RUN_MANIFEST.json
   ```

**Evidence to collect**:
- `HQE_RUN_MANIFEST.json` content.
- Manifest-validation output.

**Exit criteria**:
- [ ] `HQE_RUN_MANIFEST.json` exists and is schema-valid.

### Phase 5: Final Cross-Artifact Consistency Check

**Goal**: Ensure all artifacts reference the same facts.

1. **Verify stable IDs**: the same finding ID refers to the same issue in `HQE_FINDINGS.json`, `HQE_RISK_REGISTER.md`, `HQE_MASTER_TODO.md`, `HQE_PATTERN_FINDINGS.md`, and `HQE_REPORT.md`.
2. **Verify counts**: severity counts in the report match the manifest and findings.
3. **Verify health score** is supported by 3–5 evidence-backed reasons.
4. **Verify output caps** are respected (30/25/20).
5. **Run the protocol bundle validator**:
   ```bash
   python3 scripts/validate_protocol_bundle.py
   ```

**Evidence to collect**:
- Cross-artifact consistency checklist.
- Protocol bundle validation output.

**Exit criteria**:
- [ ] IDs, counts, and health score are consistent across artifacts.
- [ ] Protocol bundle validation passes.

## 6. Required Controls / Checks

- Validate `HQE_FINDINGS.json` against `schemas/finding.schema.json` before assembly.
- Validate semantic invariants (severity gates, taint chains, line bounds) before assembly.
- Run secret-redaction checks on all snippets before emitting artifacts.
- Ensure stable finding IDs are used consistently across every artifact.
- Respect output caps: 30 CRITICAL/HIGH total, 25 MEDIUM, 20 LOW one-liners.
- Ensure the health score is evidence-based and includes 3–5 supporting reasons.
- Do not emit empty or placeholder artifacts.

## 7. Artifact Outputs

The full artifact set for an audit run is:

- `HQE_REPORT.md` (executive summary and top-level findings)
- `HQE_FINDINGS.json` (machine-readable findings list)
- `HQE_RUN_MANIFEST.json` (run metadata, coverage, health score)
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
- `HQE_HANDOFF.md` (when remediation is requested; see [`workflows/handoff-generation.md`](handoff-generation.md))

Validate machine-readable artifacts with:

```bash
python3 scripts/validate_findings.py HQE_FINDINGS.json
python3 scripts/validate_semantics.py HQE_FINDINGS.json
python3 scripts/validate_manifest.py HQE_RUN_MANIFEST.json
python3 scripts/validate_session_log.py HQE_SESSION_LOG.json
python3 scripts/validate_protocol_bundle.py
```

## 8. Exit Criteria

Artifact generation is complete when:

- [ ] `HQE_FINDINGS.json` passes schema and semantic validation.
- [ ] All nine canonical Markdown artifacts are generated and non-empty.
- [ ] `HQE_REPORT.md` and `HQE_RUN_MANIFEST.json` are generated and consistent with findings.
- [ ] All machine-readable artifacts pass schema validation.
- [ ] Stable IDs are consistent across artifacts.
- [ ] Output caps are respected.
- [ ] No unredacted secrets appear in any artifact.
- [ ] Protocol bundle validation passes.

## 9. Confidence Model Reminders

Tag artifact-level claims:

- `[FACT]` — Counts, validation results, and command outputs observed directly.
- `[INFERENCE]` — Health score band derived from finding distributions.
- `[HYPOTHESIS]` — Claims about expected downstream impact of findings.
- `[NEEDS_VERIFICATION]` — Artifacts that could not be fully validated.

Never claim artifacts are complete or valid without running the validators and inspecting their output.
