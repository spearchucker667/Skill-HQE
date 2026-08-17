# Evidence Capture & Triad Validation Workflow

This workflow guides the host AI agent through collecting, validating, and recording evidence triads for every candidate finding.

---

## 1. Objective
Ensure 100% evidentiary compliance: zero unsubstantiated claims, verified file paths, non-empty code snippets, and automated secret redaction.

---

## 2. Evidence Triad Requirements
Every finding must include at least one valid evidence triad:
1. **Target File Path**: Exact relative path to file on disk.
2. **Line Range or Anchor**:
   - Discrete line range: `start_line >= 1` and `end_line >= start_line`.
   - Structural anchor: Symbol name (`symbol: "handle_auth"`), `anchor`, and `grep_signature`.
3. **Verifiable Code Snippet**: 2–5 lines of exact matching source code.

---

## 3. Execution Steps

### Step 1: Capture Source Snippet
Read the suspect code chunk:
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

### Step 2: Secret Redaction Pass
All captured snippets automatically run through `scripts/redact_secrets.py` regex filters. Ensure no raw credentials or tokens appear in final payloads.

### Step 3: Record Command Executions
When test or verification commands are executed, capture exit codes and outputs:
```python
store.record_tool_execution(
    tool_name="cargo_test",
    command="cargo test test_auth",
    exit_code=0,
    stdout="test test_auth ... ok"
)
```
