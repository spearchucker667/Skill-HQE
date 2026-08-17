# HQE Comprehensive Capability Mapping

This document provides a granular, evidence-backed capability mapping demonstrating source-to-skill parity between `HQE-Workbench` and `Skill-HQE`.

---

## Capability Mapping Matrix

| # | Capability Domain | Source File(s) / Section | Disposition | Target Component(s) | Validation Mechanism |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1** | **Canonical Protocol Engine** | `protocol/hqe-engineer.yaml` | **PORT** | `protocol/hqe-engineer.yaml`, `SKILL.md` | `python3 protocol/validate.py protocol/hqe-engineer.yaml` |
| **2** | **Protocol Schema Contract** | `protocol/hqe-engineer-schema.json` | **PORT** | `protocol/hqe-engineer-schema.json` | `python3 scripts/validate_protocol_bundle.py --strict-schema-metadata` |
| **3** | **Protocol Validation Suite** | `protocol/validate.py`, `protocol/verify.py` | **PORT** | `protocol/validate.py`, `protocol/verify.py` | `python3 protocol/validate.py --schema` |
| **4** | **Health Scoring System** | `protocol/hqe-engineer.yaml#health_score_rubric` | **ADAPTED** | `references/health-scoring.md`, `runtime/artifact_pipeline.py` | `pytest tests/test_protocol_skill_parity.py` |
| **5** | **Hard Constraints** | `protocol/hqe-engineer.yaml#hard_constraints` | **PORT** | `SKILL.md`, `references/evidence-standard.md` | `pytest tests/test_protocol_skill_parity.py` |
| **6** | **Severity Gate & Likelihood** | `protocol/hqe-engineer.yaml#severity_gate` | **PORT** | `references/severity-confidence-effort.md`, `schemas/finding.schema.json` | `python3 scripts/validate_semantics.py` |
| **7** | **Security Taint Chains** | `protocol/hqe-engineer.yaml#taint_chain_requirement` | **PORT** | `references/security-review.md`, `schemas/finding.schema.json` | `python3 scripts/validate_semantics.py` |
| **8** | **Change Budget & Rollback** | `protocol/hqe-engineer.yaml#change_budget` | **PORT** | `references/change-control.md`, `workflows/remediation-run.md` | `pytest tests/test_protocol_skill_parity.py` |
| **9** | **Anti-Regression Controls** | `protocol/hqe-engineer.yaml#anti_regression_rule` | **PORT** | `references/change-control.md`, `SKILL.md` | `pytest tests/test_protocol_skill_parity.py` |
| **10** | **Stop-the-Line Incident Flow** | `protocol/hqe-engineer.yaml#stop_the_line_criteria` | **PORT** | `workflows/incident-response.md`, `templates/incident-mini-report.md` | `pytest tests/test_semantics.py` |
| **11** | **No-Stall Blockers & Hypotheses** | `protocol/hqe-engineer.yaml#no_stall_rule` | **PORT** | `references/blockers-and-unknowns.md`, `templates/unknowns-verification.md` | `pytest tests/test_semantics.py` |
| **12** | **Output Caps & Overflow Control** | `protocol/hqe-engineer.yaml#output_controls` | **PORT** | `references/output-controls.md` | Profile and schema constraints |
| **13** | **Finding Taxonomy & IDs** | `protocol/hqe-engineer.yaml#definitions.id_prefixes` | **PORT** | `schemas/finding.schema.json`, `runtime/finding_registry.py` | `python3 scripts/validate_semantics.py` |
| **14** | **Deterministic Artifact Assembly** | `crates/hqe-artifacts/src/builder.rs` | **PARTIAL** | `runtime/artifact_pipeline.py`, `scripts/build_artifacts.py` | `pytest tests/test_runtime.py` |
| **15** | **Finding Registry & State Machine**| `crates/hqe-core/src/findings.rs` | **REPLACED_BY_RUNTIME** | `runtime/finding_registry.py` | `pytest tests/test_runtime.py` |
| **16** | **Session Continuity Engine** | `crates/hqe-artifacts/src/session.rs` | **NEEDS REPLACEMENT** | `runtime/session_manager.py` | `pytest tests/test_runtime.py` |
| **17** | **Evidence Collector & Store** | `crates/hqe-artifacts/src/evidence.rs` | **REPLACED_BY_RUNTIME** | `runtime/evidence_store.py` | `pytest tests/test_runtime.py` |
| **18** | **Run Manifest Generator** | `crates/hqe-artifacts/src/manifest.rs` | **REPLACED_BY_RUNTIME** | `runtime/run_manifest.py`, `scripts/create_run_manifest.py` | `pytest tests/test_runtime.py` |
| **19** | **Risk Register Deliverable** | `docs/artifact-format.md#risk-register` | **PORT** | `templates/risk-register.md`, `runtime/artifact_pipeline.py` | Structure & template check |
| **20** | **Master TODO Backlog** | `docs/artifact-format.md#master-todo` | **PORT** | `templates/master-todo-backlog.md`, `runtime/artifact_pipeline.py` | Structure & template check |
| **21** | **Pattern Findings Deliverable** | `docs/artifact-format.md#pattern-findings` | **PORT** | `templates/pattern-findings.md`, `runtime/artifact_pipeline.py` | Structure & template check |
| **22** | **Quick Wins vs Structural** | `docs/artifact-format.md#quick-wins` | **PORT** | `templates/quick-wins-vs-structural.md`, `runtime/artifact_pipeline.py` | Structure & template check |
| **23** | **Security Posture Summary** | `docs/artifact-format.md#security-posture` | **PORT** | `templates/security-posture-summary.md`, `runtime/artifact_pipeline.py` | Structure & template check |
| **24** | **Reliability Summary** | `docs/artifact-format.md#reliability-summary` | **PORT** | `templates/reliability-summary.md`, `runtime/artifact_pipeline.py` | Structure & template check |
| **25** | **Testing Gaps Deliverable** | `docs/artifact-format.md#testing-gaps` | **PORT** | `templates/testing-gaps.md`, `runtime/artifact_pipeline.py` | Structure & template check |
| **26** | **Unknowns & Verification** | `docs/artifact-format.md#unknowns` | **PORT** | `templates/unknowns-verification.md`, `runtime/artifact_pipeline.py` | Structure & template check |
| **27** | **Confidence Declaration** | `docs/artifact-format.md#confidence` | **PORT** | `templates/confidence-declaration.md`, `runtime/artifact_pipeline.py` | Structure & template check |
| **28** | **Secret Redaction Engine** | `crates/hqe-core/src/redaction.rs` | **TRANSLATE** | `scripts/redact_secrets.py`, `schemas/redaction-log.schema.json` | `pytest tests/test_redaction.py` |
| **29** | **Static Risk Scanner** | `crates/hqe-core/src/repo.rs` | **TRANSLATE** | `scripts/local_risk_scan.py` | `pytest tests/test_local_risk_scan.py` |
| **30** | **Repository Ingestion Engine** | `crates/hqe-core/src/repo.rs` | **TRANSLATE** | `scripts/inventory_repo.py`, `references/repository-orientation.md` | `pytest tests/test_inventory.py` |
| **31** | **Manifest & Tech Detection** | `crates/hqe-core/src/repo.rs` | **TRANSLATE** | `scripts/detect_manifests.py`, `scripts/detect_test_commands.py` | `pytest tests/test_manifests.py` |
| **32** | **Prompt Injection Defense** | `docs/SECURITY_MODEL.md` | **PORT** | `references/prompt-injection-defense.md` | Acceptance scenario fixture test |
| **33** | **Code Review Prompt Family** | `mcp-server/code-review.toml` | **TRANSLATE** | `workflows/security-audit.md`, `references/quality-gates.md` | Review of translated heuristics |
| **34** | **Debugging Prompt Family** | `mcp-server/cli-prompt-library/debugging/` | **TRANSLATE** | `workflows/debug-error.md`, `workflows/trace-regression.md` | Review of workflow diagnostic steps |
| **35** | **Testing Prompt Family** | `mcp-server/cli-prompt-library/testing/` | **TRANSLATE** | `references/testing-review.md`, `workflows/testing-audit.md` | Review of test-gap heuristics |
| **36** | **Architecture Prompt Family** | `mcp-server/cli-prompt-library/architecture/`| **TRANSLATE** | `references/architecture-review.md`, `workflows/architecture-audit.md` | Review of architecture heuristics |
| **37** | **Quality Evaluation Gates** | `mcp-server/prompts/server/resources/gates/` | **TRANSLATE** | `references/quality-gates.md` | Review of gate criteria |
| **38** | **Language Diagnostic Guides** | `mcp-server/prompts/` | **TRANSLATE** | `references/language-guides/*.md` (9 languages) | Structure and link checks |
| **39** | **Pre-Delivery Gates / DoD** | `protocol/hqe-engineer.yaml#pre_delivery_checklist` | **PORT** | `references/pre-delivery-gates.md` | `pytest tests/test_protocol_skill_parity.py` |
| **40** | **Source Lineage & Provenance** | Root `LICENSE`, `NOTICE`, `protocol/` | **PORT** | `docs/SOURCE_AUDIT.md`, `references/source-lineage.md` | Checksums & notice checks |
| **41** | **Desktop Application UI** | `desktop/workbench/` | **DROPPED** | None | Out of scope for headless AI skill |
| **42** | **SQLite / Keyring Persistence** | `crates/hqe-core/src/encrypted_db.rs` | **ADAPTATION REQUIRED** | None | Replaced by ephemeral JSON session logs |
| **43** | **Provider Client Adapters** | `crates/hqe-openai/` | **ACCEPTABLE** | None | Handled natively by host AI runtime |
| **44** | **MCP Orchestration** | `crates/hqe-mcp/` | **DROPPED** | None | Handled natively by host AI runtime |
