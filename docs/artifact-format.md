# HQE Artifact Format Specification

**Version**: 5.0.0  
**Status**: Canonical  
**Applies to**: All `/HQE` audit runs that emit deliverables through `runtime.artifact_pipeline`

---

## 1. Purpose

This document defines the canonical layout, naming, and schema contracts for HQE audit artifacts. It ensures that:

- Human reviewers receive consistent Markdown deliverables.
- Downstream tooling receives machine-readable JSON payloads.
- Every artifact maps to a validated JSON Schema contract in `schemas/`.
- The artifact lifecycle (template + schema + pipeline emission + test) is complete.

---

## 2. Canonical Artifact Directory Layout

An HQE run that uses `ArtifactPipeline.build_all_artifacts(output_dir)` produces the following files in the target directory:

```text
artifacts/
├── CONFIDENCE_DECLARATION.md
├── INCIDENT_MINI_REPORT.md
├── MASTER_TODO_BACKLOG.md
├── PATTERN_FINDINGS.md
├── PATCH_ACTIONS.md
├── PATCH_ACTIONS.json
├── QUICK_WINS_VS_STRUCTURAL.md
├── REDACTION_LOG.md
├── REDACTION_LOG.json
├── RELIABILITY_SUMMARY.md
├── REMEDIATION_PLAN.md
├── REMEDIATION_PLAN.json
├── REPORT.json
├── RISK_REGISTER.md
├── SECURITY_POSTURE_SUMMARY.md
├── TESTING_GAPS.md
├── UNKNOWNS_VERIFICATION.md
├── VALIDATION_REPORT.md
├── VALIDATION_REPORT.json
└── HQE_RUN_MANIFEST.json          (generated separately by runtime/run_manifest.py)
```

Markdown (`.md`) files are intended for human review. JSON (`.json`) files are machine-readable representations of the same artifact and are validated against the schemas in `schemas/`.

---

## 3. Markdown Deliverables

| File | Template | Purpose |
| :--- | :--- | :--- |
| `RISK_REGISTER.md` | [`templates/risk-register.md`](../templates/risk-register.md) | Ranked list of all findings with severity, status, and exposure. |
| `MASTER_TODO_BACKLOG.md` | [`templates/master-todo-backlog.md`](../templates/master-todo-backlog.md) | Prioritized remediation backlog (severity > confidence > effort). |
| `PATTERN_FINDINGS.md` | [`templates/pattern-findings.md`](../templates/pattern-findings.md) | Systematic patterns requiring two or more related occurrences. |
| `QUICK_WINS_VS_STRUCTURAL.md` | [`templates/quick-wins-vs-structural.md`](../templates/quick-wins-vs-structural.md) | Separation of small, localized fixes from cross-cutting work. |
| `SECURITY_POSTURE_SUMMARY.md` | [`templates/security-posture-summary.md`](../templates/security-posture-summary.md) | Active security findings and taint chains. |
| `RELIABILITY_SUMMARY.md` | [`templates/reliability-summary.md`](../templates/reliability-summary.md) | Boot and reliability findings. |
| `TESTING_GAPS.md` | [`templates/testing-gaps.md`](../templates/testing-gaps.md) | Verification debt and required test suites. |
| `UNKNOWNS_VERIFICATION.md` | [`templates/unknowns-verification.md`](../templates/unknowns-verification.md) | Hypotheses and blockers requiring live verification. |
| `CONFIDENCE_DECLARATION.md` | [`templates/confidence-declaration.md`](../templates/confidence-declaration.md) | Audit confidence breakdown by epistemic level. |
| `INCIDENT_MINI_REPORT.md` | [`templates/incident-mini-report.md`](../templates/incident-mini-report.md) | Active CRITICAL/HIGH security incidents. |
| `PATCH_ACTIONS.md` | [`templates/patch-action.md`](../templates/patch-action.md) | One patch action per open finding. |
| `REMEDIATION_PLAN.md` | [`templates/remediation-plan.md`](../templates/remediation-plan.md) | Phased remediation plan with exit criteria. |
| `VALIDATION_REPORT.md` | [`templates/validation-report.md`](../templates/validation-report.md) | Validation status for findings with verification commands. |
| `REDACTION_LOG.md` | [`templates/redaction-log.md`](../templates/redaction-log.md) | Log of secrets redacted during the audit. |

---

## 4. JSON Schema Contracts

Machine-readable artifacts validate against JSON Schema Draft-07 definitions in `schemas/`.

| Artifact | Markdown | JSON | Schema |
| :--- | :--- | :--- | :--- |
| Patch Actions | `PATCH_ACTIONS.md` | `PATCH_ACTIONS.json` | [`schemas/patch-actions.schema.json`](../schemas/patch-actions.schema.json) (collection) and [`schemas/patch-action.schema.json`](../schemas/patch-action.schema.json) (single item) |
| Remediation Plan | `REMEDIATION_PLAN.md` | `REMEDIATION_PLAN.json` | [`schemas/remediation-plan.schema.json`](../schemas/remediation-plan.schema.json) |
| Validation Report | `VALIDATION_REPORT.md` | `VALIDATION_REPORT.json` | [`schemas/validation-report.schema.json`](../schemas/validation-report.schema.json) |
| Redaction Log | `REDACTION_LOG.md` | `REDACTION_LOG.json` | [`schemas/redaction-log.schema.json`](../schemas/redaction-log.schema.json) |
| Report | — | `REPORT.json` | [`schemas/report.schema.json`](../schemas/report.schema.json) |
| Findings | — | `findings.json` (input) | [`schemas/finding.schema.json`](../schemas/finding.schema.json) and [`schemas/findings.schema.json`](../schemas/findings.schema.json) |
| Session Log | — | `HQE_SESSION_LOG.json` | [`schemas/session-log.schema.json`](../schemas/session-log.schema.json) |
| Run Manifest | — | `HQE_RUN_MANIFEST.json` | [`schemas/run-manifest.schema.json`](../schemas/run-manifest.schema.json) |

### 4.1 Validation Status Key

`validation-report.schema.json` permits only the statuses documented in [`templates/validation-report.md`](../templates/validation-report.md):

- `VERIFIED` — Fix confirmed, no regression.
- `PARTIAL` — Fix works under limited conditions; follow-up required.
- `NOT_VERIFIED` — Could not reproduce or validate.
- `REGRESSION` — Fix caused a new issue.

### 4.2 Redaction Log Schema

`redaction-log.schema.json` requires:

- `run_id`: identifier tying the log to the session or redaction run.
- `timestamp`: ISO 8601 timestamp (derived from the session when available).
- `total_redactions`: total count of redacted secrets.
- `by_type`: mapping of secret type to count.
- `redactions`: optional detailed list of `{file, secret_type, replacement}` records.

---

## 5. Pipeline Generation

Artifacts are produced deterministically by `runtime.artifact_pipeline.ArtifactPipeline`:

```python
from runtime import (
    ArtifactPipeline,
    FindingRegistry,
    SessionManager,
    TypedRedactionEngine,
)

registry = FindingRegistry()
session = SessionManager(repo_path=".")
engine = TypedRedactionEngine()

pipeline = ArtifactPipeline(
    registry,
    session=session,
    repo_name="my-repo",
    redaction_engine=engine,
)
artifacts = pipeline.build_all_artifacts(output_dir="artifacts")
```

The pipeline emits both Markdown and JSON forms for Patch Actions, Remediation Plan, Validation Report, Redaction Log, and a standalone `REPORT.json` so that human and machine consumers receive the same canonical data.

---

## 6. Example: Redaction Log JSON

```json
{
  "run_id": "hqe-session-20260817-181110",
  "timestamp": "2026-08-17T18:11:10Z",
  "total_redactions": 2,
  "by_type": {
    "AWS_ACCESS_KEY": 1,
    "SLACK_TOKEN": 1
  },
  "files_scanned": 0,
  "redactions": [
    {
      "file": "config/keys.py",
      "secret_type": "AWS_ACCESS_KEY",
      "replacement": "REDACTED_AWS_ACCESS_KEY_1"
    },
    {
      "file": "services/notifier.py",
      "secret_type": "SLACK_TOKEN",
      "replacement": "REDACTED_SLACK_TOKEN_1"
    }
  ]
}
```

---

## 7. Verification

Run the artifact schema tests after any change to the pipeline or schemas:

```bash
python3 -m pytest tests/test_artifact_schemas.py -v
```

Run the full skill integrity check:

```bash
python3 scripts/check_skill.py .
```
