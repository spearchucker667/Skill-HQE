# CI/CD Audit Workflow

The `ci` audit workflow (`/HQE ci`) verifies the security, reliability, and reproducibility of continuous integration, build, and deployment pipelines.

## Objective

Inspect CI/CD definitions and automation scripts for least-privilege violations, secret exposure, supply-chain risk, fragile steps, and unsafe release paths. Ensure pipelines are trustworthy and reproducible.

## Trigger Conditions

- User invokes `/HQE ci`.
- A new workflow, pipeline, or deployment script is added or modified.
- Privileges, secrets scopes, or third-party actions change.
- A release process fails, is compromised, or requires compliance review.
- A supply-chain advisory affects a CI tool, action, or plugin.

## Execution Model

1. **Phase 0: Pipeline Inventory**
   - Enumerate CI workflow files, deployment scripts, release definitions, and build configurations.
   - Identify triggers, runners, environments, secrets references, and artifact production steps.
   - **Exit criteria**: Complete pipeline map with ownership and sensitivity labels.

2. **Phase 1: Permission & Privilege Review**
   - Apply least privilege: verify token scopes, job permissions, runner privileges, and branch protection.
   - Flag overly permissive defaults, wildcard permissions, and privileged containers.
   - **Exit criteria**: Overprivilege findings with recommended restrictions.

3. **Phase 2: Secret Handling**
   - Ensure secrets are referenced by name only and never logged, cached, or printed.
   - Check for hardcoded credentials, plaintext environment variables, and insecure secret injection.
   - **Exit criteria**: Secret hygiene findings or clean attestation.

4. **Phase 3: Build & Test Integrity**
   - Verify jobs are isolated, reproducible, and pinned to known versions of actions, images, and tools.
   - Check artifact signing, checksum verification, and cache poisoning risks.
   - **Exit criteria**: Integrity findings with pinning or isolation recommendations.

5. **Phase 4: Deployment & Release Paths**
   - Inspect manual gates, approvals, rollback mechanisms, blue/green or canary stages, and signing steps.
   - Ensure destructive steps are gated and reversible.
   - **Exit criteria**: Deployment risk findings.

6. **Phase 5: Supply Chain & Third-Party Actions**
   - Review third-party actions, reusable workflows, and external scripts for provenance and compromise risk.
   - Verify that unpinned or mutable references are not used for security-sensitive jobs.
   - **Exit criteria**: Supply-chain findings with remediation paths.

7. **Phase 6: Validation & Artifact Generation**
   - Confirm pipeline syntax and, where possible, validate workflows locally.
   - Emit CI/CD audit artifacts.
   - **Exit criteria**: Deliverables written and pre-delivery gates satisfied.

## Required Controls / Checks

- Enforce least-privilege permissions in every workflow job.
- Pin third-party actions and container images to immutable references (commit SHAs or versioned digests).
- Ensure no secrets appear in workflow definitions, logs, or environment exports.
- Verify branch protection, required reviews, and approval gates for release workflows.
- Require reproducible builds with locked dependency versions.
- Cite exact workflow file paths, job names, step numbers, and configuration lines.
- Document supply-chain risks such as mutable action references or unverified external scripts.

## Artifact Outputs

Use the **Standard** profile for routine CI reviews and the **Exhaustive** profile for release-pipeline audits.

- `HQE_REPORT.md` (CI/CD section and executive summary)
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

- Active credentials, tokens, or private keys in workflow files or logs.
- A deployment pipeline that can be triggered by untrusted forks or unreviewed pull requests.
- A malicious or backdoored action, script, or container image in the pipeline.
- An irreversible destructive deployment step without approval or rollback.

## Confidence Model Reminders

Tag every major claim:

- `[FACT]` — Verified by reading the workflow file or pipeline output.
- `[INFERENCE]` — Strongly supported by configuration evidence.
- `[HYPOTHESIS]` — Suspected risk pending a targeted test or policy review.
- `[NEEDS_VERIFICATION]` — Cannot verify without admin access to the CI platform or runtime logs.

Never assume a pipeline is secure because it uses a well-known CI provider; verify the configuration itself.
