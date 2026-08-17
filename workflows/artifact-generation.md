# Artifact Generation & Assembly Workflow

This workflow guides the host AI agent through compiling findings and session metadata into the 9 canonical HQE deliverables.

---

## 1. Objective
Deterministically assemble verified findings into machine-readable JSON and human-readable Markdown artifacts using the `runtime.artifact_pipeline` engine.

---

## 2. Execution Steps

### Step 1: Validate Findings Collection
1. Validate JSON schema:
   ```bash
   python3 scripts/validate_findings.py findings.json
   ```
2. Validate semantic invariants (severity gates, taint chains, line bounds):
   ```bash
   python3 scripts/validate_semantics.py findings.json
   ```

### Step 2: Assemble Canonical Deliverables
1. Run the artifact builder:
   ```bash
   python3 scripts/build_artifacts.py findings.json --output-dir artifacts/
   ```
2. The pipeline deterministically generates:
   - `RISK_REGISTER.md`
   - `MASTER_TODO_BACKLOG.md`
   - `PATTERN_FINDINGS.md`
   - `QUICK_WINS_VS_STRUCTURAL.md`
   - `SECURITY_POSTURE_SUMMARY.md`
   - `RELIABILITY_SUMMARY.md`
   - `TESTING_GAPS.md`
   - `UNKNOWNS_VERIFICATION.md`
   - `CONFIDENCE_DECLARATION.md`

### Step 3: Generate Run Manifest
1. Generate `HQE_RUN_MANIFEST.json`:
   ```bash
   python3 scripts/create_run_manifest.py --findings-file findings.json --output HQE_RUN_MANIFEST.json
   ```
2. Validate the generated manifest:
   ```bash
   python3 scripts/validate_manifest.py HQE_RUN_MANIFEST.json
   ```
