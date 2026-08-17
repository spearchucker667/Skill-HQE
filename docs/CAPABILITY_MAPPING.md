# HQE Comprehensive Capability Mapping

This document provides a granular, evidence-backed capability mapping demonstrating source-to-skill parity between [HQE-Workbench](/Users/super_user/Projects/HQE-Workbench) and [Skill-HQE](/Users/super_user/Projects/Skill-HQE).

---

## Capability Mapping Matrix

| # | Capability Domain | Source File(s) / Section | Disposition | Target Component(s) | Validation Mechanism |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1** | **Canonical Protocol Engine** | `protocol/hqe-engineer.yaml` | **PORT** | `protocol/hqe-engineer.yaml`, `SKILL.md` | `python3 protocol/validate.py protocol/hqe-engineer.yaml` |
| **2** | **Protocol Schema Contract** | `protocol/hqe-engineer-schema.json` | **PORT** | `protocol/hqe-engineer-schema.json` | `python3 scripts/validate_protocol_bundle.py --strict-schema-metadata` |
| **3** | **Protocol Validation Suite** | `protocol/validate.py` | **PORT** | `protocol/validate.py`, `scripts/validate_protocol_bundle.py` | `python3 protocol/validate.py --schema` |
| **4** | **Health Scoring System** | `protocol/hqe-engineer.yaml#health_score_rubric` | **PORT** | `references/health-scoring.md`, `templates/report.md`, `schemas/report.schema.json` | `pytest tests/test_protocol_skill_parity.py` |
| **5** | **Hard Constraints** | `protocol/hqe-engineer.yaml#hard_constraints` | **PORT** | `SKILL.md`, `references/evidence-standard.md` | `pytest tests/test_protocol_skill_parity.py` |
| **6** | **Severity Gate & Likelihood** | `protocol/hqe-engineer.yaml#severity_gate` | **PORT** | `references/severity-confidence-effort.md`, `schemas/finding.schema.json` | `python3 scripts/validate_semantics.py` |
| **7** | **Security Taint Chains** | `protocol/hqe-engineer.yaml#taint_chain_requirement` | **PORT** | `references/security-review.md`, `schemas/finding.schema.json` | `python3 scripts/validate_semantics.py` |
| **8** | **Change Budget & Rollback** | `protocol/hqe-engineer.yaml#change_budget` | **PORT** | `references/change-control.md`, `workflows/remediation-run.md` | `pytest tests/test_protocol_skill_parity.py` |
| **9** | **Anti-Regression Controls** | `protocol/hqe-engineer.yaml#anti_regression_rule` | **PORT** | `references/change-control.md`, `SKILL.md` | `pytest tests/test_protocol_skill_parity.py` |
| **10** | **Stop-the-Line Incident Flow** | `protocol/hqe-engineer.yaml#stop_the_line_criteria` | **PORT** | `workflows/incident-response.md`, `templates/incident-mini-report.md` | `pytest tests/test_semantics.py` |
| **11** | **No-Stall Blockers & Hypotheses** | `protocol/hqe-engineer.yaml#no_stall_rule` | **PORT** | `references/blockers-and-unknowns.md`, `templates/unknowns-verification.md` | Review of workflow output contract |
| **12** | **Output Caps & Overflow Control** | `protocol/hqe-engineer.yaml#output_controls` | **PORT** | `references/output-controls.md` | Schema constraints and profile tests |
| **13** | **Finding Taxonomy & IDs** | `protocol/hqe-engineer.yaml#definitions.id_prefixes` | **PORT** | `schemas/finding.schema.json`, `references/hqe-protocol.md` | `python3 scripts/validate_semantics.py` |
| **14** | **Risk Register Deliverable** | `docs/artifact-format.md#risk-register` | **PORT** | `templates/risk-register.md` | Structure & template check |
| **15** | **Master TODO Backlog** | `docs/artifact-format.md#master-todo` | **PORT** | `templates/master-todo-backlog.md` | Structure & template check |
| **16** | **Pattern Findings Deliverable** | `docs/artifact-format.md#pattern-findings` | **PORT** | `templates/pattern-findings.md` | Structure & template check |
| **17** | **Quick Wins vs Structural** | `docs/artifact-format.md#quick-wins` | **PORT** | `templates/quick-wins-vs-structural.md` | Structure & template check |
| **18** | **Security Posture Summary** | `docs/artifact-format.md#security-posture` | **PORT** | `templates/security-posture-summary.md` | Structure & template check |
| **19** | **Reliability Summary** | `docs/artifact-format.md#reliability-summary` | **PORT** | `templates/reliability-summary.md` | Structure & template check |
| **20** | **Testing Gaps Deliverable** | `docs/artifact-format.md#testing-gaps` | **PORT** | `templates/testing-gaps.md` | Structure & template check |
| **21** | **Unknowns & Verification** | `docs/artifact-format.md#unknowns` | **PORT** | `templates/unknowns-verification.md` | Structure & template check |
| **22** | **Confidence Declaration** | `docs/artifact-format.md#confidence` | **PORT** | `templates/confidence-declaration.md` | Structure & template check |
| **23** | **Run Manifest Reproducibility** | `crates/hqe-artifacts/src/manifest.rs` | **PORT** | `schemas/run-manifest.schema.json`, `scripts/validate_manifest.py` | `python3 scripts/validate_manifest.py tests/fixtures/sample_manifest.json` |
| **24** | **Session Log Continuity** | `crates/hqe-artifacts/src/session.rs` | **PORT** | `schemas/session-log.schema.json`, `scripts/validate_session_log.py` | `python3 scripts/validate_session_log.py tests/fixtures/sample_session_log.json` |
| **25** | **Patch Packaging Discipline** | `protocol/hqe-engineer.yaml#immediate_actions` | **PORT** | `references/patch-packaging.md`, `templates/patch-action.md` | Structure & template check |
| **26** | **Secret Redaction Engine** | `crates/hqe-core/src/redaction.rs` | **TRANSLATE** | `scripts/redact_secrets.py`, `schemas/redaction-log.schema.json` | `pytest tests/test_redaction.py` |
| **27** | **Static Risk Scanner** | `crates/hqe-core/src/repo.rs` | **TRANSLATE** | `scripts/local_risk_scan.py` | `pytest tests/test_local_risk_scan.py` |
| **28** | **Repository Ingestion Engine** | `crates/hqe-core/src/repo.rs` | **TRANSLATE** | `scripts/inventory_repo.py`, `references/repository-orientation.md` | `pytest tests/test_inventory.py` |
| **29** | **Manifest & Tech Detection** | `crates/hqe-core/src/repo.rs` | **TRANSLATE** | `scripts/detect_manifests.py`, `scripts/detect_test_commands.py` | `pytest tests/test_manifests.py` |
| **30** | **Prompt Injection Defense** | `docs/SECURITY_MODEL.md` | **PORT** | `references/prompt-injection-defense.md` | Acceptance scenario fixture test |
| **31** | **Code Review Prompt Family** | `mcp-server/code-review.toml` | **TRANSLATE** | `workflows/security-audit.md`, `references/quality-gates.md` | Review of translated heuristics |
| **32** | **Debugging Prompt Family** | `mcp-server/cli-prompt-library/debugging/` | **TRANSLATE** | `workflows/debug-error.md`, `workflows/trace-regression.md` | Review of workflow diagnostic steps |
| **33** | **Testing Prompt Family** | `mcp-server/cli-prompt-library/testing/` | **TRANSLATE** | `references/testing-review.md`, `workflows/testing-audit.md` | Review of test-gap methodologies |
| **34** | **Architecture Prompt Family** | `mcp-server/cli-prompt-library/architecture/`| **TRANSLATE** | `references/architecture-review.md`, `workflows/architecture-audit.md` | Review of architecture heuristics |
| **35** | **Conductor Workflow** | `mcp-server/conductor/` | **TRANSLATE** | `workflows/remediation-run.md`, `references/change-control.md` | Review of planned checkpointing rules |
| **36** | **CriticalThink Reasoning** | `mcp-server/criticalthink/` | **TRANSLATE** | `references/reasoning-methodologies.md` | Review of FOCUS/5W1H frameworks |
| **37** | **Quality Evaluation Gates** | `mcp-server/prompts/server/resources/gates/` | **TRANSLATE** | `references/quality-gates.md` | Review of gate criteria |
| **38** | **Language Diagnostic Guides** | `mcp-server/prompts/` | **TRANSLATE** | `references/language-guides/*.md` (9 languages) | Structure and link checks |
| **39** | **Pre-Delivery Gates / DoD** | `protocol/hqe-engineer.yaml#pre_delivery_checklist` | **PORT** | `references/pre-delivery-gates.md` | `pytest tests/test_protocol_skill_parity.py` |
| **40** | **Source Lineage & Provenance** | Root `LICENSE`, `NOTICE`, `protocol/` | **PORT** | `docs/SOURCE_AUDIT.md`, `references/source-lineage.md` | Verification of checksums and notices |
| **41** | **Desktop Application UI** | `desktop/workbench/` | **DROP** | None | Excluded (out of scope for AI agent skill) |
| **42** | **SQLite / Keyring Persistence** | `crates/hqe-core/src/encrypted_db.rs` | **DROP** | None | Excluded (stateless agent runtime) |
| **43** | **Provider Client Adapters** | `crates/hqe-openai/` | **DROP** | None | Excluded (handled by host agent runtime) |
