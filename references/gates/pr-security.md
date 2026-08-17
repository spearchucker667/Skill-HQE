# PR Security Gate

> **Source lineage:** HQE-Workbench `mcp-server/prompts/server/resources/gates/pr-security/`. Paraphrased for HQE Skill use.

## Purpose / When to Activate

The PR Security gate blocks approval of a pull request or patch when it introduces security vulnerabilities. It is a blocking gate and must pass before merge. Activate it during PR review, incident response, or any final quality gate before delivery.

## Pass Criteria

- No hardcoded secrets or credentials in code or diffs.
- All user input is validated before use.
- Database queries are parameterized.
- Rendered content is properly escaped.
- Authentication and authorization checks exist on protected routes.
- File uploads are type-checked.
- URL parameters are escaped.

## Forbidden Patterns / Failure Modes

| Pattern | Risk |
| :--- | :--- |
| `eval(...)` | Arbitrary code execution. |
| `innerHTML = ...` | DOM-based XSS. |
| `dangerouslySetInnerHTML` | React XSS sink. |
| `SELECT * FROM` with string concatenation | SQL injection. |
| `exec(...)` / `child_process` with unsanitized input | Command injection. |
| `password=`, `secret=`, `api_key=` in source | Secret leakage. |
| `--no-verify` bypasses | Disabled security checks. |

## Activation Rules

- **Artifact types:** PR diffs, patch files, merge proposals.
- **Workflow triggers:** PR review workflow, final quality gate, security audit.
- **Explicit request:** required; this gate is invoked explicitly for diff reviews.

## Retry / Escalation Guidance

1. **First failure:** Reject the PR and require a specific fix with file:line references.
2. **Second failure (max 2 attempts):** Escalate to a security review and produce `templates/incident-mini-report.md` if secrets were exposed or an exploit path is reachable.
3. Use the failure response format: vulnerability type, location, risk level, and concrete remediation.
