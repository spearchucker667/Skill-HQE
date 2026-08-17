# Dependency Audit Workflow

The `dependencies` audit workflow (`/HQE dependencies`) analyzes the dependency tree for security vulnerabilities, license risk, maintenance status, duplication, and supply-chain exposure.

## 1. Objective

Assess the health and risk of the repository's dependencies. Demand explicit justification for any new dependency. Convert supply-chain concerns into evidence-backed findings with clear remediation paths.

## 2. Prerequisites

Before starting the dependency audit, confirm the following:

- [ ] Access to all dependency manifests and lockfiles (e.g., `package.json`, `requirements.txt`, `Cargo.lock`, `go.mod`, `pyproject.toml`).
- [ ] Access to CI/CD workflow definitions that install, cache, or publish dependencies.
- [ ] Permission to read vulnerability advisories, license databases, or SBOM tooling if available.
- [ ] A clean working directory or a defined scope of changed files for PR-based audits.
- [ ] `protocol/hqe-engineer.yaml` and `references/dependency-review.md` are available for reference.
- [ ] Schema validators in `scripts/` are runnable (`python3 scripts/validate_findings.py`, etc.).

## 3. Entry Criteria

Begin this workflow when any of the following are true:

- User invokes `/HQE dependencies`.
- A new dependency is added or proposed.
- A vulnerability advisory affects a direct or transitive dependency.
- A release, compliance review, or security audit requires a software-bill-of-materials (SBOM) check.
- Lockfiles, manifests, or vendored code change significantly.

## 4. Stop-the-Line Conditions

Immediately halt the normal audit flow and invoke [`workflows/incident-response.md`](incident-response.md) if the audit discovers:

- A dependency with a public, weaponized exploit reachable from application code.
- A malicious or compromised package in the dependency tree.
- A license conflict that legally blocks distribution or use.
- Active credentials or secrets embedded in vendored dependencies.

Flag the triggering item as `STOP-THE-LINE: [issue]` in the session log and do not proceed with normal artifact generation until incident response is complete.

## 5. Execution Model

### Phase 0: Dependency Inventory

**Goal**: Establish a complete, accurate view of every dependency.

1. **Enumerate manifests and lockfiles**:
   - Locate all package manager files in the repository.
   - Note direct, transitive, dev, optional, and peer dependencies.
2. **Distinguish dependency kinds**:
   - Separate first-party modules from third-party packages.
   - Identify vendored, forked, or locally patched dependencies.
3. **Capture version sources**:
   - Record pinned versions from lockfiles versus floating ranges in manifests.
   - Identify any unpinned or wildcard versions.

**Evidence to collect**:
- Complete dependency inventory with names, versions, and manifest locations.
- Classification table: direct / transitive / dev / vendored / patched.
- List of unpinned or floating versions.

**Exit criteria**:
- [ ] Complete dependency inventory with version sources exists.
- [ ] Vendored and patched dependencies are explicitly identified.

### Phase 1: Vulnerability Scan

**Goal**: Find known vulnerabilities and confirm whether they are exploitable.

1. **Check versions against advisories**:
   - Compare dependency versions to known vulnerability databases (e.g., OSV, CVE, GHSA).
   - Note affected version ranges and available fixes.
2. **Assess reachability**:
   - For each vulnerable dependency, trace whether the vulnerable code path is reachable from an application entry point.
   - Use import graphs, call graphs, or manual code inspection.
3. **Prioritize by exposure**:
   - Rank reachable vulnerabilities above unreachable ones.
   - Flag reachable, public exploits as stop-the-line candidates.

**Evidence to collect**:
- Vulnerability findings with advisory IDs, affected versions, and fixed versions.
- Reachability evidence (`file:line`, import chain, or call graph).
- Severity assessment with exposure justification.

**Exit criteria**:
- [ ] Vulnerability findings include reachability evidence.
- [ ] Reachable vulnerabilities are flagged with appropriate severity.

### Phase 2: License & Compliance Review

**Goal**: Ensure dependencies are compatible with the project's distribution model.

1. **Collect license metadata**:
   - Read license fields from package manifests and repository metadata.
   - Flag missing, ambiguous, or conflicting license information.
2. **Evaluate compatibility**:
   - Identify copyleft, proprietary, unlicensed, or high-risk licenses.
   - Compare against project distribution and commercial-use requirements.
3. **Check vendored code**:
   - Verify that vendored or copied code preserves required attribution and license notices.

**Evidence to collect**:
- License risk list with dependency name, version, license, and compatibility assessment.
- Compliance recommendations and blocker findings.

**Exit criteria**:
- [ ] License risk list and compliance recommendations documented.
- [ ] Any license blocker is escalated as a stop-the-line condition.

### Phase 3: Maintenance & Risk Assessment

**Goal**: Evaluate whether dependencies are healthy enough for long-term use.

1. **Review package health signals**:
   - Release cadence, maintainer activity, issue backlog, deprecation status, and fork risk.
   - Presence of a security policy, release signing, or attestation.
2. **Assess supply-chain exposure**:
   - Identify unpinned actions in CI, unverified packages, compromised upstream indicators, or typosquatting risks.
3. **Rate risk per dependency or subsystem**:
   - Assign qualitative ratings (`HIGH`, `MEDIUM`, `LOW`) based on maintenance and exposure evidence.

**Evidence to collect**:
- Risk ratings per dependency or subsystem.
- Maintenance evidence (release dates, issue counts, advisory status).
- Supply-chain exposure notes.

**Exit criteria**:
- [ ] Risk ratings exist for all direct and critical transitive dependencies.
- [ ] Supply-chain risks are documented with mitigation options.

### Phase 4: Duplication & Bloat Analysis

**Goal**: Reduce unnecessary dependency surface area.

1. **Identify overlapping libraries**:
   - Find multiple dependencies solving the same problem (e.g., multiple HTTP clients, testing frameworks, or JSON parsers).
2. **Find unused or oversized dependencies**:
   - Detect dependencies with no imports, oversized vendored bundles, or features that are never used.
3. **Propose consolidation**:
   - Recommend removal, replacement, or downgrade with impact analysis.

**Evidence to collect**:
- Consolidation candidates with usage evidence.
- Removal or replacement rationale, including transitive impact.

**Exit criteria**:
- [ ] Consolidation candidates include usage evidence and rationale.
- [ ] Transitive impact of removal/replacement is considered.

### Phase 5: New Dependency Justification

**Goal**: Ensure every new dependency is necessary and safe.

1. **For each newly added dependency, require a `[NEW_DEPENDENCY]` record** covering:
   - Purpose: what problem it solves.
   - Maintenance status: release cadence, maintainer activity, security policy.
   - Security implications: supply-chain risk, known advisories, permission requirements.
   - Alternatives considered: standard library, existing dependencies, minimal implementations.
2. **Challenge necessity**:
   - Verify the problem cannot be solved adequately with existing code or the standard library.
3. **Record decision**:
   - Flag approved dependencies and flag unjustified ones for removal.

**Evidence to collect**:
- `[NEW_DEPENDENCY]` records for every new package.
- Comparison with alternatives.

**Exit criteria**:
- [ ] Justification present for every new dependency or dependency flagged for removal.
- [ ] No new dependency is approved without explicit review.

### Phase 6: Supply-Chain Integrity

**Goal**: Verify that installs are reproducible and tamper-evident.

1. **Check lockfile integrity**:
   - Confirm lockfiles are in sync with manifests.
   - Verify checksums, hashes, or signatures where supported.
2. **Confirm reproducible installs**:
   - Run the install command in a clean environment and record the result.
   - Flag network-dependent or non-deterministic install steps.
3. **Review CI dependency handling**:
   - Check that CI uses pinned actions, verified caches, and least-privilege registries.

**Evidence to collect**:
- Lockfile-to-manifest consistency check.
- Reproducible install command and output.
- CI dependency-handling review notes.

**Exit criteria**:
- [ ] Lockfile integrity is verified or drift is documented.
- [ ] Reproducible install succeeds or blockers are recorded.

### Phase 7: Validation & Artifact Generation

**Goal**: Produce clean, consistent, and internally consistent deliverables.

1. **Deduplicate findings** by root cause.
2. **Respect output caps** per `protocol/hqe-engineer.yaml`.
3. **Emit dependency audit artifacts**.
4. **Validate** all JSON artifacts against schemas in `schemas/`.

**Evidence to collect**:
- Final artifact set.
- Schema-validation output.
- Confidence declaration and unknowns list.

**Exit criteria**:
- [ ] All deliverables written and pre-delivery gates satisfied.
- [ ] Schema validation passes.

## 6. Required Controls / Checks

- Require explicit `[NEW_DEPENDENCY]` justification before approving new packages.
- Verify lockfile-to-manifest consistency; detect unpinned or floating versions.
- Check that vulnerable dependencies are either upgraded, isolated, or proven unreachable.
- Review vendored or copied code for hidden secrets, patches, or license conflicts.
- Prefer standard-library or existing dependencies over new additions.
- Cite exact dependency names, versions, and manifest locations in findings.
- Document supply-chain risks such as unpinned actions, unverified packages, or compromised upstreams.
- Use finding IDs `SEC-XXX` for security vulnerabilities and `MAINT-XXX` for maintenance, license, and bloat findings.

## 7. Artifact Outputs

Use the **Standard** profile for routine audits and the **Exhaustive** profile for compliance or release reviews.

- `HQE_REPORT.md` (dependency section and executive summary)
- `HQE_FINDINGS.json` (machine-readable dependency findings)
- `HQE_RISK_REGISTER.md`
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

The dependency audit is complete when:

- [ ] All phases above have been executed or explicitly skipped with justification.
- [ ] Every vulnerability finding includes reachability evidence.
- [ ] New dependencies have `[NEW_DEPENDENCY]` justification or are flagged for removal.
- [ ] License and supply-chain risks are documented.
- [ ] Artifacts are emitted and schema-validated.
- [ ] Stop-the-line conditions have been checked; if triggered, incident response has been invoked.
- [ ] The session log is updated with completed, in-progress, discovered, and reprioritized items.

## 9. Confidence Model Reminders

Tag every major claim:

- `[FACT]` — Confirmed by manifest/lockfile contents or advisory database match.
- `[INFERENCE]` — Reachability or risk strongly supported by call-graph evidence.
- `[HYPOTHESIS]` — Suspected vulnerability or maintenance risk pending confirmation.
- `[NEEDS_VERIFICATION]` — Cannot verify reachability, license, or provenance with available data.

Do not recommend a dependency removal or upgrade without considering transitive impact and providing a verification command.
