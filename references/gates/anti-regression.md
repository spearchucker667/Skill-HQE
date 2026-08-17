# Anti-Regression Gate

> **Source lineage:** Derived from HQE Workbench regression-analysis workflow and Skill-HQE artifact truthfulness requirements.

## Purpose / When to Activate

The Anti-Regression gate prevents changes to Skill-HQE or to audited repositories from re-introducing known failure modes, degraded wording, or non-deterministic artifact output. Activate it before merge, before publishing audit artifacts, and after any change to `runtime/artifact_pipeline.py`, templates, or schemas.

## Pass Criteria

- All existing validation commands pass (`check_skill.py`, `validate_protocol_bundle.py`, `scan_secrets.py`).
- Generated HQE artifacts are deterministic: two runs with the same input produce identical markdown output.
- Generated artifacts do not contain overclaim wording or known anti-patterns.
- No new forbidden file patterns appear in the release package.

## Forbidden Patterns / Failure Modes

| Pattern | Risk |
| :--- | :--- |
| `No active security vulnerabilities detected` | False-perfect security claim. Use `No active security findings recorded in this audit. This is not a guarantee of complete security coverage.` |
| `All findings verified as FACT or INFERENCE` | Overstates certainty. Use `No unverified hypotheses recorded in this audit.` |
| Pattern group claiming systematic issue with only one finding | Single occurrence is not a systematic pattern. |
| Master TODO sorted only by effort | Severity/confidence context is lost. |
| Non-deterministic artifact output | Breaks reproducibility manifests and diff-based review. |

## Activation Rules

- **Artifact types:** Pull requests, release packages, generated audit deliverables.
- **Workflow triggers:** Final quality gate, release package workflow, pre-delivery checklist.
- **Explicit request:** optional; runs automatically in CI.

## Retry / Escalation Guidance

1. **First failure:** Identify the regression, revert or patch the offending change, and re-run the gate.
2. **Second failure:** Treat as a process regression; produce a `templates/incident-mini-report.md` if the regression could mislead consumers of HQE artifacts.
3. Document any intentional exception in the run manifest `unreviewed_surfaces` with a reason.
