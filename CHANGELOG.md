# Changelog

All notable changes to the Skill-HQE project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added
- `docs/LIVE_PARITY_AUDIT_2026-08-17.md`: Complete source parity audit against HQE-Workbench.
- `docs/CAPABILITY_PARITY_MATRIX.md`: Capability-by-capability parity mapping.
- `docs/artifact-format.md`: Consolidated artifact directory layout and JSON schema specification.
- Structured methodology resources: `references/gates/` (12 gate docs) and `references/methodologies/` (CAGEERF, FOCUS, 5W1H, REACT, SCAMPER, styles).
- Coverage-aware health-score computation in `runtime/health_scoring.py`; `FindingRegistry.health_score()` delegates and omits the score when coverage is unknown to avoid false-perfect claims.
- `runtime/redaction_engine.py`: typed secret taxonomy (`TypedRedactionEngine`, `classify_secret`).
- Missing artifact schemas: `incident-mini-report`, `patch-action`, `quick-wins-vs-structural`, `remediation-plan`, `validation-report`.
- Expanded `runtime/artifact_pipeline.py` to emit all 13 canonical deliverables.
- New test modules: `tests/test_protocol.py`, `tests/test_schema.py`, `tests/test_security.py`, `tests/test_ci_contracts.py`, `tests/test_evidence_disk_verification.py`, `tests/test_finding_lifecycle.py`, `tests/test_redaction.py`, `tests/test_health_scoring_coverage.py`, `tests/test_manifest_truthfulness.py`, `tests/test_artifact_truthfulness.py`, `tests/test_secret_scanner.py`, `tests/test_release_minimality.py`, `tests/test_check_skill_side_effects.py`, `tests/test_artifact_schemas.py`, `tests/test_anti_regression.py`, `tests/test_report_json.py`, `tests/test_verify_invariants.py`.
- New runtime module: `runtime/health_scoring.py`.
- New script: `scripts/scan_secrets.py` with `.secretscanignore` allowlist.
- New CI workflow: `.github/workflows/release-package.yml` builds and validates the release ZIP on every push/PR.
- New methodology resources: `references/methodologies/critical-think.md`, `references/methodologies/code-review.md`, `references/prompt-library/README.md`.
- New anti-regression gate: `references/gates/anti-regression.md`, `scripts/anti_regression_check.py`, `tests/test_anti_regression.py`, and CI step in `.github/workflows/validate-skill.yml`.
- Expanded workflow playbooks: `workflows/security-audit.md` and `workflows/incident-response.md` now provide step-by-step operational procedures.
- JSON artifact companions: `runtime/artifact_pipeline.py` now emits `PATCH_ACTIONS.json`, `REMEDIATION_PLAN.json`, `VALIDATION_REPORT.json`, and `REDACTION_LOG.json` validated against their schemas.
- v3 HQE Report JSON renderer: `runtime/artifact_pipeline.py` now emits `REPORT.json` matching `schemas/report.schema.json` (Workbench `HqeReport` model). Tests: `tests/test_report_json.py`.
- Optional tooling: `.actionlint.yaml`, `.pre-commit-config.yaml`, and `scripts/verify_invariants.sh`. Excluded from release packages.
- New fixture: `tests/fixtures/missing-deps-fixture/`.
- Local risk scan hardening: path-traversal guard, prompt-injection marker detection, TODO/FIXME/HACK marker detection.

### Fixed
- `Finding.from_dict`/`CodeEvidence.from_dict` and `FindingRegistry.load_many` replace the duplicated inline finding loaders in `scripts/build_artifacts.py` and `scripts/create_run_manifest.py`; loading now preserves evidence verification state (`verified`, `verification_method`, `verified_at`, `source_hash`) that the inline loaders silently dropped.
- `.github/workflows/security-scan.yml` now uses `scripts/scan_secrets.py`, reporting `path:line:TYPE` without leaking potential secrets and supporting fixture allowlists.
- `.github/workflows/validate-skill.yml` now installs dev dependencies before running `check_skill.py`.
- `protocol/README.md` no longer references non-existent Rust CLI scripts.
- `protocol/hqe-schema.json` examples updated from stale v3/v4 to v5.0.0 and dual-schema roles documented.
- `pyproject.toml` switched to PEP 639 `license = "Apache-2.0"` with `license-files`. Build configured with `packages = []` for skill metadata-only install.
- `scripts/check_skill.py` no longer writes `__pycache__` into the repository during Python syntax checks.
- `runtime/run_manifest.py` now derives protocol version from `protocol/hqe-engineer.yaml`, defaults coverage to truthful `reviewed=false`/`depth=unknown`, preserves structured `command_records`, and emits coverage-aware health scores.
- `runtime/artifact_pipeline.py` now prioritizes Master TODO by severity > confidence > effort, requires ≥2 occurrences for pattern groups, and softens overclaim wording in security/unknowns artifacts.
- `scripts/package_skill.py` now excludes `build/`, `dist/`, and `*.egg-info` in addition to macOS/archive/test debris.
- `runtime/finding_registry.py` now serializes findings schema-totally (`validation`/`related_findings` always emitted) and validates the serialized finding against `schemas/finding.schema.json` at registration/update, closing the runtime/schema split-brain that caused delayed artifact failures.
- `runtime/finding_registry.py`: `merge()` now uses ordered deduplication instead of `list(set(...))` for deterministic artifact output.
- `runtime/evidence_store.py`: anchor verification now supports multi-line 2–5 line snippets and requires the snippet to contain the anchor; symbol/grep_signature disk verification now checks the submitted snippet against disk content, so fabricated snippets cannot pass a disk-verification request.
- `runtime/artifact_pipeline.py`: remediation plans now sort by severity rank (CRITICAL → HIGH → MEDIUM → LOW → INFO) instead of alphabetically; patch actions (markdown and JSON) now only include open findings.
- `runtime/session_manager.py`: session logs now serialize/restore lifecycle `state`; `reprioritized` matches `session-log.schema.json` (array of strings); added `SessionManager.load_from_file()`/`from_dict()`.
- `scripts/scan_secrets.py`: allowlist entries now honor exact paths, directory prefixes (`tests/`), and glob patterns instead of only `endswith`; removed the dead `KNOWN_TEST_TOKENS` mechanism.
- `scripts/check_protocol_sync.py`: removed stale `HQE_PROTOCOL_SKILL_EMBED_PACKAGE` logic; a missing `SOURCE_CHECKSUMS.sha256` is now a hard failure.
- `scripts/create_run_manifest.py`: `--health-score` now defaults to a truthful coverage-aware calculation; findings load/validation failures are fatal unless `--best-effort` is passed.
- `scripts/build_artifacts.py`: `--session-file` now actually loads and restores the session (identity, timestamps, state, progress) instead of creating a fresh session.
- `scripts/validate_protocol_bundle.py`: strict metadata mode now asserts the protocol `license` matches `pyproject.toml` (Apache-2.0).
- Protocol metadata corrected to Apache-2.0 (`protocol/hqe-engineer.yaml`) to match `LICENSE`, `pyproject.toml`, README, and NOTICE.
- Tests migrated to v5 lifecycle (`VERIFIED`/`OPEN`/`DEFERRED` instead of `FIXED`/`REOPENED`/`SUPERSEDED`) and v5 health bands; credential detection vectors are now constructed at runtime from nonmatching fragments so the repository contains no literal credential patterns.
- CI hardening: all four workflows declare `permissions: contents: read` and `persist-credentials: false`; actions upgraded to Node 24 runtimes (`checkout@v5`, `setup-python@v6`, `upload-artifact@v5`); independent CI gates run with `if: always()`; `requirements-dev.txt` is pinned to exact versions.
- README CI badge is now live GitHub Actions status instead of a hard-coded green badge.

### Changed
- 21 workflow playbooks expanded for depth and consistency, covering every workflow in `workflows/`.
- SKILL.md frontmatter `name` normalized to `hqe` to match the documented lowercase install directory (`~/.agents/skills/hqe`); skill loaders require the directory name and the frontmatter `name` to match.
- `README.md`, `CONTRIBUTING.md`, `SECURITY.md` updated to reflect current runtime, artifact model, and validation commands.

---

## [5.0.0] - 2026-08-17

### Added
- **Unified HQE Control-Plane v5.0.0**: Upgraded protocol engine to HQE Engineer Protocol v5.0.0 (`protocol/hqe-engineer.yaml`), JSON Schema Draft 2020-12 (`protocol/hqe-engineer-schema.json`), and validator suite (`protocol/validate.py`, `protocol/verify.py`).
- **Deterministic Python Runtime Layer (`runtime/`)**:
  - `runtime/session_manager.py`: State machine enforcing session lifecycles and persistence (`HQE_SESSION_LOG.json`).
  - `runtime/finding_registry.py`: Invariant enforcement, finding deduplication, lifecycle transitions (`CONFIRMED`, `FIXED`, `SUPERSEDED`), and severity gate validation.
  - `runtime/evidence_store.py`: Code evidence triad verification (`path`, line ranges/anchors, snippet) and automated deterministic secret redaction.
  - `runtime/run_manifest.py`: Reproducibility run manifest generator capturing environment and coverage metrics.
  - `runtime/artifact_pipeline.py`: Deterministic assembly engine for the 9 canonical audit deliverables.
- **Protocol Synchronization Tooling**: Added `scripts/check_protocol_sync.py` and `tests/test_protocol_sync.py` to continuously enforce protocol checksum stability.
- **Workflow & Template Contracts**: Added `tests/test_workflow_contracts.py` and `tests/test_template_contracts.py` verifying structural compliance of all 21 workflows and 19 templates.
- **Comprehensive Documentation Modernization**:
  - Rewrote `README.md` to answer "What happens when you run /HQE" and document all 17 operational modes.
  - Rewrote `docs/USER_GUIDE.md` and `docs/DEVELOPER_GUIDE.md` into exhaustive operator and extension manuals.
  - Rewrote `docs/ARCHITECTURE.md` with updated system layers, sequence diagrams, and runtime state machines.
  - Added ADR-006 to `docs/DESIGN_DECISIONS.md`.
  - Created `docs/REPOSITORY_AUDIT.md` and `docs/REPOSITORY_HYGIENE_REPORT.md`.

### Changed
- Cleaned up transient agent handoff prompts and staging directories (`HQE_SKILL_AGENT_HANDOFF.md`, `HQE_SKILL_CONVERSION_PROMPT.md`, `HQE_SKILL_PARITY_REPAIR_AGENT_HANDOFF.md`, `HQE_PROTOCOL_SKILL_EMBED_PACKAGE/`).
- Enforced strict `.gitignore` rules against `__pycache__`, `*.pyc`, and `.pytest_cache`.
- Added CI `git clean validation` quality gate in `.github/workflows/ci.yml`.
- Standardized all documentation headers and fixtures to HQE Protocol v5.0.0.


## [4.2.1] - 2026-08-17

### Added
- **Canonical Protocol Embedding**: Embedded active HQE Protocol v4.2.1 (`protocol/hqe-engineer.yaml`), Draft-7 JSON Schema (`protocol/hqe-engineer-schema.json`), protocol validator (`protocol/validate.py`), and repository-level validator (`scripts/validate_protocol_bundle.py`).
- **Control Plane Restoration**: Restored 1–10 health scoring system (`references/health-scoring.md`), severity gates for CRITICAL/HIGH findings, security taint chains, change budgets ($\le 5$ files), anti-regression rules (`[BEHAVIOR CHANGE]`, `[NEW_DEPENDENCY]`), stop-the-line incident handling, and no-stall blocker instrumentation.
- **Canonical Artifacts**: Added complete templates and schemas for all 9 canonical HQE audit deliverables: Risk Register, Master TODO Backlog, Pattern Findings, Quick Wins vs Structural Work, Security Posture Summary, Reliability Summary, Testing Gaps, Unknowns & Verification, and Confidence Declaration.
- **Helper Utilities**:
  - `scripts/local_risk_scan.py`: Safe, read-only static risk scanner ported from `crates/hqe-core/src/repo.rs`.
  - `scripts/validate_semantics.py`: Semantic cross-field invariant validator for findings and manifests.
  - `scripts/package_skill.py`: Release packager strictly excluding git metadata and cache debris.
- **Quality Gates & Reasoning**: Added `references/quality-gates.md`, `references/reasoning-methodologies.md`, `references/output-controls.md`, `workflows/debug-error.md`, and `workflows/trace-regression.md`.
- **Test Suite**: Expanded test suite covering structure, schema validation, semantic rules, local risk scanning, inventory classification, manifest detection across 22+ ecosystems, redaction, link validity, packaging hygiene, protocol contract, and acceptance scenarios.

### Fixed
- Fixed Phase -1 vs Phase 0 ordering conflict in `SKILL.md`.
- Restored `NEEDS_VERIFICATION` to confidence vocabulary across `SKILL.md`, references, and schemas.
- Fixed inventory file coverage undercounting by tracking all repository files and classifying binary/media/archive artifacts.
- Fixed manifest detection silent truncation by returning exact counts and truncation flags.
- Reconciled schema metadata `$id` and `title` to v4.2.1.
- Repaired relative Markdown links in `docs/` and `references/`.
- Replaced deprecated `RefResolver` with modern `referencing` API and fail-closed validation.

---

## [1.0.0] - 2026-02-06
- Initial conversion skeleton of HQE skill for agentic runtimes.
