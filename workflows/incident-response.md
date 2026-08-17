# Incident Response Workflow

This workflow is activated by stop-the-line criteria during any HQE audit or by explicit invocation when a security incident is suspected. It replaces normal audit outputs with an `HQE_INCIDENT_MINI_REPORT.md` and, if needed, a focused remediation run.

## 1. Objective

Contain active or imminent harm, eradicate the root cause, recover to a known-good state, verify the fix, and capture lessons learned. Preserve evidence without exposing secrets.

## 2. Trigger Conditions

Activate this workflow immediately upon any of the following:

- Active incidents, ongoing exploitation, or crash loops.
- Committed or leaked credentials, API keys, tokens, or private keys.
- Backdoor, malicious workflow, or remote-code-execution evidence.
- Critical data-loss or corruption paths that are reachable.
- Cases where critical verification is impossible due to missing source context.
- Any finding flagged as `STOP-THE-LINE: [issue]` by another workflow.

## 3. Prerequisites

Before executing incident response, confirm:

- [ ] The triggering evidence is captured and its location recorded (`file:line` or `anchor+grep`).
- [ ] Secret redaction rules are active; no raw credentials will be printed.
- [ ] `templates/incident-mini-report.md` is available.
- [ ] Contact/escalation paths are known (repository maintainer, security team, incident commander).
- [ ] Write access is limited to the minimum set of files required for containment.

## 4. Entry Criteria

This workflow may begin when:

- A stop-the-line condition from `workflows/security-audit.md` or any other workflow is met.
- The user explicitly invokes `/HQE incident-response` or equivalent.
- Automated tooling or manual inspection reveals active exploitation indicators.

## 5. Phase 1: Immediate Containment

**Goal**: Stop the bleeding without destroying evidence.

1. **Declare the incident**.
   - Record the incident ID, timestamp, and triggering finding ID.
   - Update the session log with `STOP-THE-LINE: [issue]` and the affected paths.
2. **Protect secrets**.
   - If credentials are exposed, immediately redact them in any generated artifacts.
   - Do **not** commit rotation commands or new secrets into the repository.
3. **Disable the vulnerable path** where safe and possible:
   - Revoke/rotate exposed tokens, keys, or passwords.
   - Disable malicious or compromised workflows, actions, or integrations.
   - Restrict permissions on affected accounts, branches, or infrastructure.
   - Block suspicious network egress or ingress if within scope.
4. **Preserve evidence**:
   - Capture the current state of affected files before changing them.
   - Save logs, CI outputs, or scan results that show the incident.
   - Do not delete commit history unless explicitly authorized.

**Evidence to collect**:
- Impacted paths with `file:line` or `anchor+grep`.
- Indicators (secrets, backdoor signatures, workflow abuse patterns).
- Containment actions taken and timestamps.

**Exit criteria**:
- [ ] The incident is declared in the session log.
- [ ] Affected paths are identified and documented.
- [ ] Immediate containment actions are recorded.
- [ ] No raw secrets remain in any artifact.

## 6. Phase 2: Eradication

**Goal**: Remove the root cause of the incident.

1. **Remove malicious code or configuration**:
   - Delete backdoors, malicious payloads, and unauthorized workflow modifications.
   - Revert unauthorized commits or changes to a known-good state.
2. **Remove leaked secrets from source history**:
   - Use repository-secret-removal tooling (e.g., `git-filter-repo`, BFG Repo-Cleaner) only when explicitly authorized.
   - Document the commit range that contained the secret.
3. **Close vulnerable code paths**:
   - Add input validation, authorization checks, or sanitization at the root-cause location.
   - Apply the minimal safe change; avoid broad refactors during incident response.
4. **Update trust boundaries**:
   - If the incident crossed a trust boundary, document the gap and the control added.

**Evidence to collect**:
- Diff of eradication changes.
- `file:line` references for every removed or hardened component.
- Confirmation that the secret, backdoor, or vulnerable path no longer exists (e.g., `grep` results).

**Exit criteria**:
- [ ] Root cause is removed or hardened.
- [ ] No indicators of compromise remain in the reviewed scope.
- [ ] Eradication changes are documented.

## 7. Phase 3: Recovery

**Goal**: Return the repository and related systems to normal operation safely.

1. **Restore from known-good state** where applicable:
   - Roll back to the last verified-good commit or branch.
   - Re-run build, test, and lint commands to confirm baseline health.
2. **Re-enable services with safeguards**:
   - Re-enable workflows, integrations, or deployments only after verification.
   - Apply temporary monitoring or approval gates if residual risk remains.
3. **Rotate all potentially affected credentials**:
   - Generate new secrets outside the repository.
   - Update secret stores, CI variables, and runtime configuration.
   - Verify the old credentials are invalidated.
4. **Communicate status**:
   - Notify affected stakeholders with a concise status update.
   - Do not disclose secret values, weaponized details, or unverified hypotheses.

**Evidence to collect**:
- Recovery actions and timestamps.
- Build/test command outputs showing restored health.
- Confirmation of credential rotation and invalidation.

**Exit criteria**:
- [ ] Known-good state is restored or validated.
- [ ] Affected credentials are rotated and old values invalidated.
- [ ] Stakeholders are notified.

## 8. Phase 4: Verification

**Goal**: Prove the incident is resolved and cannot reoccur via the same path.

1. **Confirm eradication**:
   - Re-run the scan or command that originally detected the issue.
   - Confirm the indicator no longer appears.
2. **Confirm containment holds**:
   - Verify affected paths remain disabled or hardened.
   - Verify no new unauthorized changes have appeared.
3. **Run regression checks**:
   - Execute the project test suite or a focused subset covering the affected area.
   - Confirm no new failures were introduced by recovery actions.
4. **Validate secrets hygiene**:
   - Re-run secret-scanning tools if available.
   - Confirm no remaining plaintext secrets in the reviewed scope.

**Evidence to collect**:
- Verification commands and outputs.
- Test results.
- Secret-scan results.

**Exit criteria**:
- [ ] Detection command no longer reproduces the incident.
- [ ] Tests pass (or failures are documented and accepted).
- [ ] No residual plaintext secrets are found in scope.

## 9. Phase 5: Post-Incident Capture

**Goal**: Document the incident, response, and follow-up actions for future audits.

1. **Produce `HQE_INCIDENT_MINI_REPORT.md`** using `templates/incident-mini-report.md`:
   - **Impacted paths**: Files, workflows, secrets, or infrastructure affected.
   - **Evidence**: Anchored snippets, logs, scan results, and command outputs.
   - **Indicators**: What signaled the incident (secret leak, backdoor signature, etc.).
   - **Containment**: Steps taken to limit damage.
   - **Eradication**: Root cause removed.
   - **Recovery**: Systems returned to normal operation.
   - **Verification**: Proof the incident is resolved.
   - **Blockers**: Anything preventing full resolution.
   - **Resume criteria**: Conditions under which normal auditing can resume.
2. **Update the risk register**:
   - Add or update entries for the incident root cause and residual risk.
3. **Update the session log**:
   - Record completed containment, eradication, recovery, verification, and post-incident capture.
4. **Define follow-up actions**:
   - Long-term fixes, monitoring, or policy changes required beyond the immediate incident.

**Evidence to collect**:
- Completed incident mini-report.
- Updated risk register and session log.
- Follow-up action list with owners and due dates.

**Exit criteria**:
- [ ] `HQE_INCIDENT_MINI_REPORT.md` is generated and internally consistent.
- [ ] Risk register and session log reflect the incident.
- [ ] Follow-up actions are captured and prioritized.

## 10. Stop-the-Line Conditions Within This Workflow

If, during incident response, any of the following occur, escalate immediately and do not resume normal auditing:

- The incident expands in scope (additional secrets, systems, or users affected).
- A root cause cannot be identified and verification is impossible.
- Legal, regulatory, or organizational policy requires external notification.
- The response action risks breaking production systems.

Document the escalation in the incident mini-report and pause until authorized.

## 11. Required Controls / Checks

- Never output raw credentials, tokens, or private keys in any artifact.
- Do not weaponize exploit details; describe attack paths conceptually.
- Preserve evidence before modifying files.
- Use minimal safe changes during eradication.
- Tag all claims with `[FACT]`, `[INFERENCE]`, or `[HYPOTHESIS]`.
- Record every containment, eradication, recovery, and verification action with a timestamp.

## 12. Artifact Outputs

The primary output of this workflow is:

- `HQE_INCIDENT_MINI_REPORT.md`

Supporting artifacts that may be updated or created:

- `HQE_RISK_REGISTER.md`
- `HQE_SESSION_LOG.json`
- `HQE_FINDINGS.json` (if new findings are discovered during response)
- `HQE_HANDOFF.md` (if remediation beyond incident response is required)

Validate machine-readable artifacts with:

```bash
python3 scripts/validate_findings.py HQE_FINDINGS.json
python3 scripts/validate_manifest.py HQE_RUN_MANIFEST.json
python3 scripts/validate_session_log.py HQE_SESSION_LOG.json
```

## 13. Exit Criteria

Incident response is complete when:

- [ ] The incident is contained, eradicated, and recovered.
- [ ] Verification proves the incident path is closed.
- [ ] `HQE_INCIDENT_MINI_REPORT.md` is complete.
- [ ] No raw secrets remain in any artifact.
- [ ] The session log is updated.
- [ ] Normal HQE auditing resumes only when resume criteria are met.

## 14. Resume Criteria for Normal Auditing

Normal auditing may resume when all of the following are true:

- The incident mini-report is finalized.
- Containment and eradication are verified.
- No stop-the-line conditions remain active.
- Any newly introduced fixes or controls are included in the audit scope.
