# Dependency Audit Workflow

The `dependencies` audit workflow (`/HQE dependencies`) analyzes the dependency tree for security vulnerabilities, license risk, maintenance status, duplication, and supply-chain exposure.

## Objective

Assess the health and risk of the repository's dependencies. Demand explicit justification for any new dependency. Convert supply-chain concerns into evidence-backed findings with clear remediation paths.

## Trigger Conditions

- User invokes `/HQE dependencies`.
- A new dependency is added or proposed.
- A vulnerability advisory affects a direct or transitive dependency.
- A release, compliance review, or security audit requires a software-bill-of-materials (SBOM) check.
- Lockfiles, manifests, or vendored code change significantly.

## Execution Model

1. **Phase 0: Dependency Inventory**
   - Enumerate manifests and lockfiles (e.g., `package.json`, `requirements.txt`, `Cargo.lock`, `go.mod`, `pyproject.toml`).
   - Distinguish direct, transitive, dev, and vendored dependencies.
   - **Exit criteria**: Complete dependency inventory with version sources.

2. **Phase 1: Vulnerability Scan**
   - Check dependency versions against known vulnerability databases and advisories.
   - Confirm whether vulnerable code paths are reachable from application entrypoints.
   - **Exit criteria**: Vulnerability findings with reachability evidence.

3. **Phase 2: License & Compliance Review**
   - Review dependency licenses for compatibility with the project's distribution model.
   - Flag copyleft, proprietary, or unlicensed packages.
   - **Exit criteria**: License risk list and compliance recommendations.

4. **Phase 3: Maintenance & Risk Assessment**
   - Evaluate package health: release cadence, maintainer activity, issue backlog, deprecation status, and fork risk.
   - **Exit criteria**: Risk ratings per dependency or subsystem.

5. **Phase 4: Duplication & Bloat Analysis**
   - Identify multiple libraries solving the same problem, oversized vendored bundles, and unused dependencies.
   - **Exit criteria**: Consolidation candidates with removal or replacement rationale.

6. **Phase 5: New Dependency Justification**
   - For every newly added dependency, require a `[NEW_DEPENDENCY]` record covering purpose, maintenance status, security implications, and alternatives considered.
   - **Exit criteria**: Justification present or dependency flagged for removal.

7. **Phase 6: Validation & Artifact Generation**
   - Verify lockfile integrity and reproducible installs.
   - Emit dependency audit artifacts.
   - **Exit criteria**: Deliverables written and pre-delivery gates satisfied.

## Required Controls / Checks

- Require explicit `[NEW_DEPENDENCY]` justification before approving new packages.
- Verify lockfile-to-manifest consistency; detect unpinned or floating versions.
- Check that vulnerable dependencies are either upgraded, isolated, or proven unreachable.
- Review vendored or copied code for hidden secrets, patches, or license conflicts.
- Prefer standard-library or existing dependencies over new additions.
- Cite exact dependency names, versions, and manifest locations in findings.
- Document supply-chain risks such as unpinned actions, unverified packages, or compromised upstreams.

## Artifact Outputs

Use the **Standard** profile for routine audits and the **Exhaustive** profile for compliance or release reviews.

- `HQE_REPORT.md` (dependency section and executive summary)
- `HQE_FINDINGS.json`
- `HQE_RISK_REGISTER.md`
- `HQE_PATTERN_FINDINGS.md`
- `HQE_MASTER_TODO.md`
- `HQE_UNKNOWNS.md`
- `HQE_CONFIDENCE.md`
- `HQE_RUN_MANIFEST.json`
- `HQE_SESSION_LOG.json`
- `HQE_HANDOFF.md` (when remediation is requested)

## Stop-the-Line Conditions

Invoke `workflows/incident-response.md` if the audit discovers:

- A dependency with a public, weaponized exploit reachable from application code.
- A malicious or compromised package in the dependency tree.
- A license conflict that legally blocks distribution or use.
- Active credentials or secrets embedded in vendored dependencies.

## Confidence Model Reminders

Tag every major claim:

- `[FACT]` — Confirmed by manifest/lockfile contents or advisory database match.
- `[INFERENCE]` — Reachability or risk strongly supported by call-graph evidence.
- `[HYPOTHESIS]` — Suspected vulnerability or maintenance risk pending confirmation.
- `[NEEDS_VERIFICATION]` — Cannot verify reachability, license, or provenance with available data.

Do not recommend a dependency removal or upgrade without considering transitive impact and providing a verification command.
