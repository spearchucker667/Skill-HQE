# Documentation Audit Workflow

The `docs` audit workflow (`/HQE docs`) verifies that documentation matches implementation, remains complete, and accurately describes security, privacy, and operational concerns.

## Objective

Identify gaps, stale instructions, and contradictions between documentation and executable reality. Ensure guides are trustworthy and do not contain unsafe instructions or exposed secrets.

## Trigger Conditions

- User invokes `/HQE docs`.
- A major feature, API, or configuration change is released.
- Onboarding friction, support tickets, or contributor confusion suggest doc drift.
- A security, privacy, or compliance review requires documentation verification.
- `AGENTS.md`, `CONTRIBUTING.md`, or other governance docs are updated.

## Execution Model

1. **Phase 0: Documentation Inventory**
   - List README files, user guides, developer guides, API docs, inline comments, and governance docs.
   - Note generated docs and distinguish them from hand-maintained docs.
   - **Exit criteria**: Documented map of all docs and their owners/last-update hints.

2. **Phase 1: Implementation Parity**
   - Compare documented setup steps, configuration options, API signatures, and examples to actual code and config.
   - Flag outdated parameters, removed commands, renamed symbols, and obsolete screenshots.
   - **Exit criteria**: Stale or incorrect documentation findings.

3. **Phase 2: Completeness & Accuracy**
   - Verify that prerequisites, environment variables, build steps, test commands, and deployment procedures are complete and runnable.
   - Check that code examples compile or execute as written.
   - **Exit criteria**: Completeness gaps with severity and fix suggestions.

4. **Phase 3: Security & Privacy Documentation**
   - Review `SECURITY.md`, `PRIVACY.md`, data-handling sections, and trust-boundary descriptions.
   - Ensure reported security controls actually exist in code.
   - **Exit criteria**: Security and privacy doc gaps.

5. **Phase 4: Developer & User Experience**
   - Review `CONTRIBUTING.md`, troubleshooting guides, error-message catalogs, and UX copy.
   - Look for contradictory instructions or missing escalation paths.
   - **Exit criteria**: DX/UX documentation findings.

6. **Phase 5: Consolidation & Artifact Generation**
   - Group related doc gaps by root cause.
   - Emit documentation audit artifacts.
   - **Exit criteria**: Deliverables written and pre-delivery gates satisfied.

## Required Controls / Checks

- Cite exact doc file paths, section names, and the corresponding implementation anchors.
- Validate that code examples and commands produce the documented results when run safely.
- Redact any secrets that appear in examples or screenshots.
- Flag any documentation that instructs disabling security checks or exposing credentials.
- Update `AGENTS.md` or governance docs if repository conventions changed during the audit.
- Do not rely on external-only knowledge; verify every claim against the repository.

## Artifact Outputs

Use the **Standard** profile for focused doc reviews and the **Exhaustive** profile for release or compliance reviews.

- `HQE_REPORT.md` (documentation section and executive summary)
- `HQE_FINDINGS.json`
- `HQE_PATTERN_FINDINGS.md`
- `HQE_MASTER_TODO.md`
- `HQE_UNKNOWNS.md`
- `HQE_CONFIDENCE.md`
- `HQE_RUN_MANIFEST.json`
- `HQE_SESSION_LOG.json`
- `HQE_HANDOFF.md` (when remediation is requested)

## Stop-the-Line Conditions

Invoke `workflows/incident-response.md` if the documentation audit reveals:

- Active credentials, tokens, or private keys embedded in documentation or screenshots.
- Documentation that instructs users to disable authentication, ignore security warnings, or expose sensitive endpoints.
- A privacy or security claim that is materially false and could lead to compliance violations.

## Confidence Model Reminders

Tag every major claim:

- `[FACT]` — Directly verified by comparing doc text to code or by running a documented command.
- `[INFERENCE]` — Strongly indicated by doc drift or missing sections.
- `[HYPOTHESIS]` — Suspected inaccuracy that needs a runnable reproduction.
- `[NEEDS_VERIFICATION]` — Cannot verify without executing commands in a specific environment.

Never report doc accuracy as fact without anchoring it to a concrete doc section and implementation location.
