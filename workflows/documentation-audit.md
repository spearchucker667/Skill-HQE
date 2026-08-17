# Documentation Audit Workflow

The `docs` audit workflow (`/HQE docs`) verifies that documentation matches implementation, remains complete, and accurately describes security, privacy, and operational concerns.

## 1. Objective

Identify gaps, stale instructions, and contradictions between documentation and executable reality. Ensure guides are trustworthy and do not contain unsafe instructions or exposed secrets.

## 2. Prerequisites

Before starting the documentation audit, confirm the following:

- [ ] Access to all hand-maintained documentation, generated docs, README files, inline comments, and governance docs.
- [ ] Access to the implementation files, configuration files, and scripts that the docs describe.
- [ ] A clean working directory or a defined scope of changed files for PR-based audits.
- [ ] `protocol/hqe-engineer.yaml` and `references/documentation-review.md` are available for reference.
- [ ] Schema validators in `scripts/` are runnable (`python3 scripts/validate_findings.py`, etc.).

## 3. Entry Criteria

Begin this workflow when any of the following are true:

- User invokes `/HQE docs`.
- A major feature, API, or configuration change is released.
- Onboarding friction, support tickets, or contributor confusion suggest doc drift.
- A security, privacy, or compliance review requires documentation verification.
- `AGENTS.md`, `CONTRIBUTING.md`, or other governance docs are updated.

## 4. Stop-the-Line Conditions

Immediately halt the normal audit flow and invoke [`workflows/incident-response.md`](incident-response.md) if the documentation audit reveals:

- Active credentials, tokens, or private keys embedded in documentation or screenshots.
- Documentation that instructs users to disable authentication, ignore security warnings, or expose sensitive endpoints.
- A privacy or security claim that is materially false and could lead to compliance violations.

Flag the triggering item as `STOP-THE-LINE: [issue]` in the session log and do not proceed with normal artifact generation until incident response is complete.

## 5. Execution Model

### Phase 0: Documentation Inventory

**Goal**: Establish a complete map of documentation assets.

1. **List documentation files**:
   - README files, user guides, developer guides, API docs, architecture docs, runbooks, and governance docs.
2. **Distinguish generated from hand-maintained docs**:
   - Note which docs are generated from code and which must be updated manually.
3. **Capture ownership and freshness hints**:
   - Record last-update dates, authors, or sections that mention specific versions.
4. **Classify doc types**:
   - User-facing, contributor-facing, operator-facing, security/privacy, and generated reference.

**Evidence to collect**:
- Documented map of all docs and their owners/last-update hints.
- Classification table: hand-maintained / generated / governance / API reference.

**Exit criteria**:
- [ ] A documented map of all docs exists.
- [ ] Generated docs are distinguished from hand-maintained docs.

### Phase 1: Implementation Parity

**Goal**: Find stale or incorrect documentation.

1. **Compare setup and build instructions**:
   - Walk through documented setup steps and compare them to actual scripts and configuration.
   - Flag missing, renamed, or removed commands.
2. **Compare configuration options**:
   - Verify documented environment variables, flags, and config keys match the code.
3. **Compare API signatures and examples**:
   - Check that documented endpoints, function signatures, parameters, and return values match implementation.
4. **Compare screenshots and diagrams**:
   - Flag obsolete screenshots, outdated UI labels, or diagrams that no longer reflect the system.

**Evidence to collect**:
- Stale or incorrect documentation findings with doc section and implementation anchors.
- Code snippets showing the actual behavior alongside the stale doc text.

**Exit criteria**:
- [ ] Stale or incorrect documentation findings are documented.
- [ ] Each finding cites the doc location and the corresponding implementation location.

### Phase 2: Completeness & Accuracy

**Goal**: Verify that documentation covers what users need to know.

1. **Check prerequisites**:
   - Ensure required tools, versions, accounts, and permissions are listed.
2. **Check build, test, and deployment procedures**:
   - Verify steps are complete and runnable.
3. **Check code examples**:
   - Attempt to run or compile documented examples when safe.
   - Flag examples that fail or omit required context.
4. **Check troubleshooting and error messages**:
   - Ensure common failures have documented resolutions or escalation paths.

**Evidence to collect**:
- Completeness gaps with severity and fix suggestions.
- Command outputs from running documented examples.

**Exit criteria**:
- [ ] Completeness gaps are documented with severity and fix suggestions.
- [ ] Code examples are verified or their unverified status is noted.

### Phase 3: Security & Privacy Documentation

**Goal**: Ensure security and privacy claims are accurate and safe.

1. **Review `SECURITY.md` and `PRIVACY.md`**:
   - Confirm reported security controls exist in code.
   - Verify data-handling claims match implementation.
2. **Check trust-boundary descriptions**:
   - Ensure documented boundaries match the actual architecture.
3. **Check for unsafe instructions**:
   - Flag documentation that tells users to disable checks, expose endpoints, or share credentials.
4. **Review incident and escalation paths**:
   - Ensure security contacts and escalation procedures are current.

**Evidence to collect**:
- Security and privacy doc gaps with doc section and code anchor.
- List of unsafe instructions or materially false claims.

**Exit criteria**:
- [ ] Security and privacy doc gaps are documented.
- [ ] Unsafe instructions are flagged as findings.

### Phase 4: Developer & User Experience

**Goal**: Find friction and contradictions in contributor and user docs.

1. **Review `CONTRIBUTING.md`**:
   - Verify workflow steps match CI, lint, test, and commit conventions.
2. **Review troubleshooting guides**:
   - Look for contradictory instructions or missing escalation paths.
3. **Review error-message catalogs and UX copy**:
   - Ensure messages are accurate and actionable.
4. **Check onboarding path**:
   - Identify steps that are unclear, out of order, or missing.

**Evidence to collect**:
- DX/UX documentation findings with doc section references.
- Contradictions between docs and actual process.

**Exit criteria**:
- [ ] DX/UX documentation findings are documented.
- [ ] Contradictions are anchored to specific doc sections.

### Phase 5: Governance & Convention Sync

**Goal**: Ensure governance docs stay aligned with repository conventions.

1. **Compare `AGENTS.md` to actual conventions**:
   - If the audit changed conventions, update `AGENTS.md` or related governance docs.
2. **Check `CHANGELOG.md` and release notes**:
   - Verify notable changes are documented accurately.
3. **Check license and attribution files**:
   - Ensure `LICENSE`, `NOTICE`, and third-party attribution are complete and current.
4. **Review code-of-conduct and privacy policies**:
   - Confirm contact information and procedures are current.

**Evidence to collect**:
- Governance doc update findings.
- List of docs that need synchronization with implementation reality.

**Exit criteria**:
- [ ] Governance gaps are documented with owner and update actions.
- [ ] Any convention change from the audit is reflected in governance docs.

### Phase 6: Consolidation & Artifact Generation

**Goal**: Produce clean, consistent, and internally consistent deliverables.

1. **Group related doc gaps by root cause**:
   - Combine multiple stale sections caused by the same API change or rename.
2. **Deduplicate findings** and respect output caps.
3. **Emit documentation audit artifacts**.
4. **Validate** all JSON artifacts against schemas in `schemas/`.

**Evidence to collect**:
- Final artifact set.
- Schema-validation output.
- Confidence declaration and unknowns list.

**Exit criteria**:
- [ ] All deliverables written and pre-delivery gates satisfied.
- [ ] Schema validation passes.

## 6. Required Controls / Checks

- Cite exact doc file paths, section names, and the corresponding implementation anchors.
- Validate that code examples and commands produce the documented results when run safely.
- Redact any secrets that appear in examples or screenshots.
- Flag any documentation that instructs disabling security checks or exposing credentials.
- Update `AGENTS.md` or governance docs if repository conventions changed during the audit.
- Do not rely on external-only knowledge; verify every claim against the repository.
- Use finding IDs `DX-XXX` for developer/user-experience issues and `MAINT-XXX` for maintenance/governance issues.

## 7. Artifact Outputs

Use the **Standard** profile for focused doc reviews and the **Exhaustive** profile for release or compliance reviews.

- `HQE_REPORT.md` (documentation section and executive summary)
- `HQE_FINDINGS.json` (machine-readable documentation findings)
- `HQE_PATTERN_FINDINGS.md`
- `HQE_MASTER_TODO.md`
- `HQE_UNKNOWNS.md`
- `HQE_CONFIDENCE.md`
- `HQE_RUN_MANIFEST.json`
- `HQE_SESSION_LOG.json`
- `HQE_HANDOFF.md` (when remediation is requested)

Validate machine-readable artifacts with:

```bash
python3 scripts/validate_findings.py HQE_FINDINGS.json
python3 scripts/validate_manifest.py HQE_RUN_MANIFEST.json
python3 scripts/validate_session_log.py HQE_SESSION_LOG.json
```

## 8. Exit Criteria

The documentation audit is complete when:

- [ ] All phases above have been executed or explicitly skipped with justification.
- [ ] Every doc gap cites the doc section and corresponding implementation anchor.
- [ ] Security and privacy claims are verified against code.
- [ ] Artifacts are emitted and schema-validated.
- [ ] Stop-the-line conditions have been checked; if triggered, incident response has been invoked.
- [ ] The session log is updated with completed, in-progress, discovered, and reprioritized items.

## 9. Confidence Model Reminders

Tag every major claim:

- `[FACT]` — Directly verified by comparing doc text to code or by running a documented command.
- `[INFERENCE]` — Strongly indicated by doc drift or missing sections.
- `[HYPOTHESIS]` — Suspected inaccuracy that needs a runnable reproduction.
- `[NEEDS_VERIFICATION]` — Cannot verify without executing commands in a specific environment.

Never report doc accuracy as fact without anchoring it to a concrete doc section and implementation location.
