# Changelog

All notable changes to the Skill-HQE project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [5.0.0] - 2026-08-17

### Added
- **Unified HQE Control-Plane v5.0.0**: Upgraded protocol engine to HQE Engineer Protocol v5.0.0 (`protocol/hqe-engineer.yaml`), JSON Schema Draft 2020-12 (`protocol/hqe-engineer-schema.json`), and validator suite (`protocol/validate.py`, `protocol/verify.py`).
- **Control Plane Enforcement**: Fully consolidated health scoring, severity gates with likelihood/exposure models, trust-boundary analysis, security taint tracking, change budgets ($\le 5$ files), behavior-change detection (`[BEHAVIOR CHANGE]`), anti-regression enforcement, stop-the-line incident handling, no-stall blocker instrumentation, and reproducibility manifests.
- **Finding Lifecycle & Artifact Taxonomy**: Added finding lifecycle states (`CONFIRMED`, `STRONGLY_SUPPORTED`, `SUSPECTED`, `NOT_REPRODUCED`, `FIXED`, `REOPENED`, `SUPERSEDED`) and canonical artifact taxonomy across all 9 audit deliverables.
- **Dynamic Schema Validation**: Upgraded schema validation tooling to automatically support JSON Schema Draft 2020-12.

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
