# HQE Skill Repository Audit & Hygiene Inventory

**Audit Date**: 2026-08-17  
**Audited Target**: `/Users/super_user/Projects/Skill-HQE/`  
**Protocol Version**: HQE Engineer Protocol v5.0.0 (`protocol/hqe-engineer.yaml`)  
**Repository Version**: 5.0.0 (`VERSION`)

---

## 1. Executive Summary

This repository audit documents the structural, documentation, and asset state of **Skill-HQE** prior to the Phase 1–9 hygiene and modernization pass. The objective is to transition Skill-HQE from a converted workbench archive containing migration debris into a pristine, production-grade AI skill repository.

---

## 2. Current Structure & Inventory

The repository currently contains 12 top-level domains:

1. `.` (Root): Entrypoint `SKILL.md`, `README.md`, `LICENSE`, `NOTICE`, `VERSION`, `CHANGELOG.md`, `CONTRIBUTING.md`, `SECURITY.md`, `CODE_OF_CONDUCT.md`, `PRIVACY.md`, `TERMS_OF_SERVICE.md`, `pyproject.toml`, `requirements-dev.txt`, alongside several transient agent handoff prompts.
2. `protocol/`: Embedded canonical HQE Protocol v5.0.0 assets (`hqe-engineer.yaml`, `hqe-engineer-schema.json`, `hqe-schema.json`, `validate.py`, `verify.py`, `SOURCE_CHECKSUMS.sha256`, `TARGET_CHECKSUMS.sha256`, `README.md`, `VALIDATORS.md`, `HQE_v5_MIGRATION_NOTES.md`).
3. `references/`: 26 modular reference guides + `references/language-guides/` (9 polyglot language diagnostic guides).
4. `workflows/`: 21 operational workflows covering all audit, remediation, incident response, verification, and runtime execution procedures.
5. `templates/`: 19 markdown artifact and deliverable templates.
6. `schemas/`: 7 JSON Schema Draft-07 machine-readable contract definitions.
7. `runtime/`: 6 deterministic execution engine modules (`__init__.py`, `session_manager.py`, `finding_registry.py`, `evidence_store.py`, `run_manifest.py`, `artifact_pipeline.py`).
8. `scripts/`: 16 standalone Python 3.10+ CLI helper utilities.
9. `tests/`: 18 pytest test suites + unit fixtures + polyglot acceptance test repos (`tests/acceptance/fixtures/`).
10. `docs/`: 10 architectural, migration, capability, security, threat model, and guide documents.
11. `.github/`: CI/CD workflows (`ci.yml`, `security-scan.yml`, `validate-skill.yml`).
12. `HQE_PROTOCOL_SKILL_EMBED_PACKAGE/`: Transient staging bundle from previous embedding pass.

---

## 3. Identified Deficiencies & Findings

### 3.1 Duplicated Files

| Duplicate Asset | Canonical Location | Redundant Location(s) | Action |
| :--- | :--- | :--- | :--- |
| **Protocol Files** | `protocol/hqe-engineer.yaml`<br>`protocol/hqe-engineer-schema.json`<br>`protocol/validate.py` | `HQE_PROTOCOL_SKILL_EMBED_PACKAGE/canonical-protocol/*`<br>`HQE_PROTOCOL_SKILL_EMBED_PACKAGE/drop-in/protocol/*` | Remove staging package; keep `protocol/` as single source of truth |
| **Protocol Checksums** | `protocol/SOURCE_CHECKSUMS.sha256` | `protocol/TARGET_CHECKSUMS.sha256`<br>`HQE_PROTOCOL_SKILL_EMBED_PACKAGE/SOURCE_PROTOCOL_SHA256SUMS.txt` | Consolidate onto canonical `protocol/SOURCE_CHECKSUMS.sha256` |
| **Legacy Protocol Assets** | `protocol/hqe-schema.json`<br>`protocol/verify.py` | `HQE_PROTOCOL_SKILL_EMBED_PACKAGE/optional-legacy-protocol/*` | Retain active files in `protocol/`; remove staging copies |

### 3.2 Misplaced Files

| File / Path | Current Location | Issue | Target Resolution |
| :--- | :--- | :--- | :--- |
| `HQE_SKILL_AGENT_HANDOFF.md` | Root `/` | Historical conversion prompt transcript | Remove from root |
| `HQE_SKILL_CONVERSION_PROMPT.md` | Root `/` | Historical conversion prompt transcript | Remove from root |
| `HQE_SKILL_PARITY_REPAIR_AGENT_HANDOFF.md` | Root `/` | Historical parity repair prompt transcript | Remove from root |
| `HQE_PROTOCOL_SKILL_EMBED_PACKAGE/` | Root `/` | Staging bundle from packaging step | Remove staging directory; sync scripts |

### 3.3 Stale Documentation

| Document | Stale Reference | Required Update |
| :--- | :--- | :--- |
| `README.md` | References `v4.2.1` in tree and badges | Update to `v5.0.0` and reflect complete `runtime/` engine |
| `docs/ARCHITECTURE.md` | Claims `Protocol Version: v4.2.1`; outdated tree diagram | Update to `v5.0.0`; document runtime state machine and complete file tree |
| `docs/DESIGN_DECISIONS.md` | Contains ADR-005 referencing schema v4.2.1 reconciliation | Add ADR-006 documenting protocol v5.0.0 upgrade and deterministic runtime layer |
| `docs/FINDING_SPECIFICATION.md` | Claims `Protocol Version: v4.2.1` | Update to `v5.0.0` and reflect finding schema fields |
| `docs/SECURITY_MODEL.md` | Claims `Protocol Version: v4.2.1` | Update to `v5.0.0` |
| `references/audit-methodology.md` | Claims `Protocol Version: v4.2.1` | Update to `v5.0.0` |
| `tests/fixtures/sample_report.json` | Claims `protocol_version: "4.2.1"` | Update to `"5.0.0"` |

### 3.4 Missing / Underdeveloped Documentation

| Document | Current State | Required Enhancement |
| :--- | :--- | :--- |
| `docs/USER_GUIDE.md` | 101 lines (basic outline) | Expand into comprehensive manual detailing all modes, options, expected deliverables, and step-by-step agent instructions. |
| `docs/DEVELOPER_GUIDE.md` | 38 lines (very brief) | Expand into in-depth extension guide covering schemas, runtime layer, custom workflows, test writing, and release packaging. |
| `docs/ARCHITECTURE.md` | 125 lines (missing runtime engine details) | Add comprehensive architectural diagrams, state machine flows, evidence pipeline, and progressive disclosure model. |
| `docs/REPOSITORY_HYGIENE_REPORT.md` | Missing | Create upon completion of Phase 1–8. |

### 3.5 Unused Assets & Generated Files

- `.pytest_cache/` directory in root.
- Python bytecode files (`*.pyc`) inside `tests/acceptance/fixtures/large_repo/__pycache__/` and `tests/acceptance/fixtures/malicious_repo_prompt/__pycache__/`.
- `.gitignore` needs to ensure fixtures do not track bytecode while allowing fixture source files.

### 3.6 Files Requiring Review & Adjustment

- `scripts/check_protocol_sync.py`: Validate `protocol/` against `protocol/SOURCE_CHECKSUMS.sha256` as the single canonical source.
- `scripts/check_skill.py`: Clean up exclusion list for removed staging paths; ensure all new docs are validated.
- `scripts/package_skill.py`: Remove exclusions for removed staging folders.
- `tests/test_links.py`: Ensure all links in rewritten docs and references resolve cleanly.

---

## 4. Remediation Plan by Phase

1. **Phase 1**: Define final architecture and normalize structure.
2. **Phase 2**: Remove transient staging packages and obsolete prompt handoffs; clean test fixture bytecode.
3. **Phase 3**: Rewrite and modernize all core documentation (`README.md`, `SKILL.md`, `docs/USER_GUIDE.md`, `docs/DEVELOPER_GUIDE.md`, `docs/ARCHITECTURE.md`, `CHANGELOG.md`, `CONTRIBUTING.md`, `SECURITY.md`, `CODE_OF_CONDUCT.md`).
4. **Phase 4**: Ensure `protocol/` is the single canonical source of truth with verified checksums.
5. **Phase 5**: Scan for and remove TODOs, obsolete comments, and stale references across the codebase.
6. **Phase 6**: Update `.gitignore` and verify clean repository state.
7. **Phase 7**: Execute full validation suite (`pytest`, `check_skill.py`, `validate_protocol_bundle.py`, `check_protocol_sync.py`, `compileall`).
8. **Phase 8**: Validate 100% of relative markdown links.
9. **Phase 9**: Generate final `docs/REPOSITORY_HYGIENE_REPORT.md`.
