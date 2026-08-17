# Security Awareness Gate

> **Source lineage:** HQE-Workbench `mcp-server/prompts/server/resources/gates/security-awareness/`. Paraphrased for HQE Skill use.

## Purpose / When to Activate

The Security Awareness gate prevents common, easily introduced vulnerabilities in code and configuration. Activate it whenever the agent is generating, editing, or reviewing code, scripts, or infrastructure definitions where untrusted input, credentials, or network communication may appear.

Use this gate as a lightweight first line of defense before the heavier [PR Security](pr-security.md) gate is applied to a diff.

## Pass Criteria

- No hardcoded secrets, passwords, API keys, tokens, or credentials in source.
- All user input is validated and sanitized before processing.
- Database queries use parameterized or prepared statements.
- Authentication and authorization checks are present on protected paths.
- Network communication uses HTTPS/TLS.
- APIs include rate limiting.
- Security events are logged without exposing sensitive data.
- Dependencies are kept current and scanned for known vulnerabilities.

## Forbidden Patterns / Failure Modes

| Pattern | Risk |
| :--- | :--- |
| `password="..."`, `api_key="..."`, `secret="..."`, `token="..."` | Hardcoded credential exposure. |
| `password123`, `admin123`, `root:root` | Weak/default credentials. |
| `SELECT * FROM` concatenated with variables | SQL injection. |
| Missing input validation | Injection, path traversal, or unsafe deserialization. |
| Plain HTTP URLs for sensitive traffic | Man-in-the-middle exposure. |
| Verbose error messages leaked to clients | Information disclosure. |

## Activation Rules

- **Artifact types:** source code, configuration files, shell scripts, infrastructure templates.
- **Workflow triggers:** code-generation tasks, remediation patches, local risk scans, debugging sessions.
- **Explicit request:** not required; this gate runs automatically on code-category prompts.

## Retry / Escalation Guidance

1. **First failure:** Remove the forbidden pattern, replace secrets with environment-variable references or secret-store lookups, and add validation.
2. **Second failure (max 2 attempts):** Escalate to [PR Security](pr-security.md) for a full taint-chain review.
3. If a secret may have been committed, follow the stop-the-line protocol in `references/security-review.md` and rotate the credential.
