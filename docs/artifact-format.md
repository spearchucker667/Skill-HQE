# HQE Artifact Format Specification

This document describes the canonical artifact layout produced by the HQE `/HQE` skill. All artifacts are deterministic, versioned, and validated against JSON Schemas in `schemas/`.

---

## Artifact Directory Layout

A complete HQE audit run produces a directory (default `artifacts/`) containing:

```text
artifacts/
├── HQE_REPORT.md                 # Executive summary (human-readable)
├── HQE_FINDINGS.json             # Machine-readable findings collection
├── HQE_RUN_MANIFEST.json         # Reproducibility manifest
├── HQE_SESSION_LOG.json          # Cross-run session log
├── HQE_REDACTION_LOG.json        # Secret redaction ledger
├── RISK_REGISTER.md              # Prioritized risk table
├── MASTER_TODO_BACKLOG.md        # Prioritized remediation backlog
├── PATTERN_FINDINGS.md           # Cross-cutting systematic patterns
├── QUICK_WINS_VS_STRUCTURAL.md   # Effort-sorted work split
├── SECURITY_POSTURE_SUMMARY.md   # Security findings summary
├── RELIABILITY_SUMMARY.md        # Reliability/boot findings summary
├── TESTING_GAPS.md               # Required verification suites
├── UNKNOWNS_VERIFICATION.md      # Hypotheses needing verification
├── CONFIDENCE_DECLARATION.md     # Fact/inference/hypothesis breakdown
├── INCIDENT_MINI_REPORT.md       # Active CRITICAL/HIGH security incidents
├── PATCH_ACTIONS.md              # One patch per finding
├── REMEDIATION_PLAN.md           # Phased remediation plan
└── VALIDATION_REPORT.md          # Verification run results
```

---

## Machine-Readable JSON Artifacts

### `HQE_RUN_MANIFEST.json`

Validated by `schemas/run-manifest.schema.json`.

Key fields:

| Field | Type | Description |
| --- | --- | --- |
| `run_id` | string | Unique run identifier. |
| `timestamps` | object | `start` and `end` ISO-8601 timestamps. |
| `repository_details` | object | `commit`, `path`, and optional branch/tag. |
| `protocol_details` | object | HQE protocol name and version. |
| `summary` | object | Counts of total, critical, high, medium, low, and info findings. |
| `health_score` | object | `score` (1-10), `band`, `omitted` flag, and `reasons`. |

Example:

```json
{
  "run_id": "hqe-run-20260817-123456",
  "timestamps": {
    "start": "2026-08-17T12:34:56+00:00",
    "end": "2026-08-17T12:35:12+00:00"
  },
  "repository_details": {
    "commit": "abc123...",
    "path": "/path/to/repo"
  },
  "protocol_details": {
    "name": "HQE Engineer Protocol",
    "version": "5.0.0"
  },
  "summary": {
    "total_files_scanned": 120,
    "total_findings": 5,
    "critical_findings": 1,
    "high_findings": 2,
    "medium_findings": 1,
    "low_findings": 1,
    "info_findings": 0
  },
  "health_score": {
    "score": 6,
    "band": "Adequate",
    "omitted": false,
    "reasons": ["Evaluated against HQE v5 rubric"]
  }
}
```

### `HQE_FINDINGS.json`

Validated by `schemas/findings.schema.json` (collection) and `schemas/finding.schema.json` (item).

Each finding includes:

| Field | Required | Description |
| --- | --- | --- |
| `id` | yes | `HQE-<CATEGORY>-<INDEX>` |
| `title` | yes | Short finding title. |
| `category` | yes | One of BOOT, SEC, BUG, REL, PERF, UX, DX, DOC, DEBT, DEPS. |
| `severity` | yes | CRITICAL, HIGH, MEDIUM, LOW, INFO. |
| `confidence` | yes | FACT, INFERENCE, HYPOTHESIS, NEEDS_VERIFICATION. |
| `status` | yes | CONFIRMED, STRONGLY_SUPPORTED, SUSPECTED, NOT_REPRODUCED, FIXED, REOPENED, SUPERSEDED. |
| `affected_component` | yes | File path, module, or subsystem. |
| `evidence` | yes | Array of `CodeEvidence` objects. |
| `observed_behavior` | yes | What the code actually does. |
| `expected_behavior` | yes | What the code should do. |
| `root_cause` | yes | Why the issue exists. |
| `impact` | yes | Concrete impact statement. |
| `remediation` | yes | Minimal-change fix. |
| `effort` | yes | S, M, or L. |
| `regression_risk` | yes | Risk of the fix causing regressions. |
| `preconditions` | CRITICAL/HIGH | Conditions required for exploitation/failure. |
| `exploitability` | CRITICAL/HIGH | How easily the issue can be triggered. |
| `blast_radius` | CRITICAL/HIGH | Scope of impact. |
| `likelihood` | CRITICAL/HIGH | Likelihood of occurrence. |
| `likelihood_justification` | CRITICAL/HIGH | Evidence for likelihood. |
| `exposure_evidence` | CRITICAL/HIGH | Proof of exposure. |
| `taint_chain` | SEC CRITICAL/HIGH | Source → transforms → validation boundary → sink → impact. |

### `HQE_SESSION_LOG.json`

Validated by `schemas/session-log.schema.json`. Tracks session state transitions, discovered findings, tool executions, and next-session notes.

### `HQE_REDACTION_LOG.json`

Validated by `schemas/redaction-log.schema.json`. Records every secret redaction with type, replacement token, and source file.

---

## Markdown Deliverables

Each `.md` deliverable has a matching template in `templates/` and a JSON schema in `schemas/` for machine validation:

| Markdown File | Template | Schema |
| --- | --- | --- |
| `RISK_REGISTER.md` | `templates/risk-register.md` | `schemas/risk-register.schema.json` |
| `MASTER_TODO_BACKLOG.md` | `templates/master-todo-backlog.md` | `schemas/master-todo.schema.json` |
| `PATTERN_FINDINGS.md` | `templates/pattern-findings.md` | `schemas/pattern-findings.schema.json` |
| `QUICK_WINS_VS_STRUCTURAL.md` | `templates/quick-wins-vs-structural.md` | `schemas/quick-wins-vs-structural.schema.json` |
| `SECURITY_POSTURE_SUMMARY.md` | `templates/security-posture-summary.md` | `schemas/security-posture.schema.json` |
| `RELIABILITY_SUMMARY.md` | `templates/reliability-summary.md` | `schemas/reliability-summary.schema.json` |
| `TESTING_GAPS.md` | `templates/testing-gaps.md` | `schemas/testing-gaps.schema.json` |
| `UNKNOWNS_VERIFICATION.md` | `templates/unknowns-verification.md` | `schemas/unknowns.schema.json` |
| `CONFIDENCE_DECLARATION.md` | `templates/confidence-declaration.md` | `schemas/confidence-declaration.schema.json` |
| `INCIDENT_MINI_REPORT.md` | `templates/incident-mini-report.md` | `schemas/incident-mini-report.schema.json` |
| `PATCH_ACTIONS.md` | `templates/patch-action.md` | `schemas/patch-action.schema.json` |
| `REMEDIATION_PLAN.md` | `templates/remediation-plan.md` | `schemas/remediation-plan.schema.json` |
| `VALIDATION_REPORT.md` | `templates/validation-report.md` | `schemas/validation-report.schema.json` |

---

## Validation

To validate the artifact format of an HQE run:

```bash
python3 scripts/validate_findings.py artifacts/HQE_FINDINGS.json
python3 scripts/validate_manifest.py artifacts/HQE_RUN_MANIFEST.json
python3 scripts/validate_session_log.py artifacts/HQE_SESSION_LOG.json
```

---

## Versioning

Artifact schemas use JSON Schema Draft-07 and are versioned with the HQE Protocol. When the protocol version in `VERSION` changes, update schema metadata and regenerate fixtures/tests as needed.
