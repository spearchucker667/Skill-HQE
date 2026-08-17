# HQE Capability Parity Matrix

**Target:** `spearchucker667/Skill-HQE` (portable `/HQE` skill)  
**Reference:** `HQE-Workbench` (reference engineering implementation)  
**Date:** 2026-08-17  
**Version:** Skill-HQE 5.0.0

---

## Legend

| Status | Meaning |
|--------|---------|
| ✅ Complete | Capability is present and validated in Skill-HQE. |
| 🟡 Partial | Capability exists but is incomplete, stubbed, or lacks depth. |
| ❌ Missing | Capability is not present in Skill-HQE. |
| ⚪ N/A | Application-specific runtime; not appropriate to port. |

---

## Required HQE Controls

| Workbench Capability | Skill Status | Missing / Gap | Action |
|----------------------|--------------|---------------|--------|
| **Canonical HQE Protocol v5.0.0** | ✅ Complete | None. `protocol/hqe-engineer.yaml` and schema are canonical. | Keep in sync with Workbench protocol changes. |
| **Severity gates (CRITICAL/HIGH/MEDIUM/LOW/INFO)** | ✅ Complete | Enforced in `runtime/finding_registry.py` and schemas. | None. |
| **Confidence model (FACT/INFERENCE/HYPOTHESIS/NEEDS_VERIFICATION)** | ✅ Complete | Defined in protocol and templates. | None. |
| **Likelihood / exposure reasoning** | ✅ Complete | Required by `finding.schema.json` for HIGH+ findings. | None. |
| **Trust-boundary analysis** | ✅ Complete | Required by protocol and `security-posture.schema.json`. | None. |
| **Taint chains (source → transformation → validation → sink)** | ✅ Complete | Required by protocol and `finding.schema.json`. | None. |
| **Change budgets** | ✅ Complete | Protocol defines effort tiers; templates reference them. | None. |
| **Anti-regression rules** | 🟡 Partial | Present in references but no automated anti-regression gate. | Add a reference gate doc and consider a script check. |
| **Stop-the-line conditions** | 🟡 Partial | Defined in protocol; workflow playbooks vary in depth. | Expand workflow stubs. |
| **No-stall rules** | 🟡 Partial | Policy exists; operational enforcement depends on workflow depth. | Expand workflows. |
| **Reproducibility manifests** | ✅ Complete | `runtime/run_manifest.py` emits `HQE_RUN_MANIFEST.json`. | None. |
| **Evidence requirements** | ✅ Complete | Evidence triad enforced in `runtime/evidence_store.py`. | None. |
| **Artifact lifecycle (template + schema + validator + doc + test)** | 🟡 Partial | Most artifacts covered; a few templates lack schemas. | Create missing schemas and pipeline emission. |
| **Health scoring** | ❌ Missing | Rubric in protocol but no runtime calculation. | Add `FindingRegistry.health_score()` and manifest field. |

---

## Methodology & Reasoning

| Workbench Capability | Skill Status | Missing / Gap | Action |
|----------------------|--------------|---------------|--------|
| **Structured gates (security-awareness, code-quality, technical-accuracy, test-coverage, pr-security, etc.)** | ❌ Missing | Only summary in `references/quality-gates.md`. | Create `references/gates/*.md` translations. |
| **Structured methodologies (CAGEERF, FOCUS, 5W1H, SCAMPER, etc.)** | ❌ Missing | Only summary in `references/reasoning-methodologies.md`. | Create `references/methodologies/*.md` translations. |
| **Response styles (analytical, creative, procedural, reasoning)** | ❌ Missing | Not present. | Add `references/methodologies/styles.md` if needed. |
| **Prompt template library (33+ single-shot prompts)** | ❌ Missing | No prompt library. | Create `references/prompt-library/README.md` index. |
| **Security/taint-analysis prompts** | ❌ Missing | No equivalent to `cli-security/commands/security/*.toml`. | Add security prompt methodology to `references/security-heuristics.md`. |
| **Conductor multi-turn workflow prompts** | ❌ Missing | No equivalent. | Document in `references/escalation-patterns.md` or new file. |
| **Critical-think critique rubric** | ❌ Missing | No equivalent. | Add `references/methodologies/critical-think.md`. |
| **Code-review prompt with severity classification** | ❌ Missing | No equivalent. | Add `references/methodologies/code-review.md`. |

---

## Runtime & Scanning

| Workbench Capability | Skill Status | Missing / Gap | Action |
|----------------------|--------------|---------------|--------|
| **Integrated scan pipeline** | 🟡 Partial | Split across scripts; no single `ScanPipeline` class. | Acceptable for portable skill; consider documenting pipeline. |
| **Repo scanner (entrypoints, tech stack, TODO markers, backup files)** | 🟡 Partial | `inventory_repo.py` and `local_risk_scan.py` cover parts; TODO/backup detection missing. | Add TODO/FIXME/HACK marker detection to `local_risk_scan.py`. |
| **Local-only analysis fallback** | ✅ Complete | `local_risk_scan.py` is read-only and local. | None. |
| **Secret redaction engine** | 🟡 Partial | Regex redaction works but lacks typed taxonomy and exclusion helpers. | Add `runtime/redaction_engine.py` with `SecretType` taxonomy. |
| **System-prompt integrity verification** | ⚪ N/A | Workbench desktop/CLI runtime feature. | Not appropriate for portable skill. |
| **Jailbreak / encoded-attack detection** | ⚪ N/A | Workbench desktop/CLI runtime feature. | Not appropriate for portable skill; defense policy exists in `references/prompt-injection-defense.md`. |
| **SQLite semantic cache** | ⚪ N/A | Workbench desktop/CLI runtime feature. | Not appropriate for portable skill. |
| **Encrypted chat database** | ⚪ N/A | Workbench desktop/CLI runtime feature. | Not appropriate for portable skill. |
| **OpenAI-compatible client / provider profiles** | ⚪ N/A | Application runtime; skill is provider-independent. | Not appropriate for portable skill. |
| **Vector/embeddings placeholder** | ⚪ N/A | Application runtime. | Not appropriate for portable skill. |

---

## Artifacts & Reports

| Workbench Capability | Skill Status | Missing / Gap | Action |
|----------------------|--------------|---------------|--------|
| **Risk Register** | ✅ Complete | Template, schema, and tests present. | None. |
| **Master TODO** | ✅ Complete | Template, schema, and tests present. | None. |
| **Pattern Findings** | ✅ Complete | Template, schema, and tests present. | None. |
| **Quick Wins vs Structural Work** | ✅ Complete | Template and schema present. | None. |
| **Security Summary / Security Posture** | ✅ Complete | Template and schema present. | None. |
| **Reliability Summary** | ✅ Complete | Template and schema present. | None. |
| **Testing Gaps** | ✅ Complete | Template and schema present. | None. |
| **Unknowns / Verification** | ✅ Complete | Template and schema present. | None. |
| **Confidence Declaration** | ✅ Complete | Template and schema present. | None. |
| **Run Manifest** | ✅ Complete | Generated by `runtime/run_manifest.py`. | Add `health_score` field. |
| **Session Log** | ✅ Complete | Generated by `runtime/session_manager.py`. | None. |
| **Redaction Log** | 🟡 Partial | Template exists; JSON writer and schema need verification. | Verify schema + add writer if missing. |
| **v3 Report (`report.md` 8-section)** | 🟡 Partial | `report.md` template exists; no `report.json` renderer matching Workbench `HqeReport` model. | Document in `docs/artifact-format.md`. |
| **Patch Action** | 🟡 Partial | Template exists; schema and pipeline emission unverified. | Create schema + pipeline step. |
| **Remediation Plan** | 🟡 Partial | Template exists; schema and pipeline emission unverified. | Create schema + pipeline step. |
| **Validation Report** | 🟡 Partial | Template exists; schema and pipeline emission unverified. | Create schema + pipeline step. |
| **Incident Mini-Report** | 🟡 Partial | Template exists; schema and pipeline emission unverified. | Create schema + pipeline step. |

---

## Validation & CI/CD

| Workbench Capability | Skill Status | Missing / Gap | Action |
|----------------------|--------------|---------------|--------|
| **Protocol YAML validation** | ✅ Complete | `protocol/validate.py`, `protocol/verify.py`. | None. |
| **Protocol bundle validation** | ✅ Complete | `scripts/validate_protocol_bundle.py`. | None. |
| **Checksum sync validation** | ✅ Complete | `scripts/check_protocol_sync.py`. | None. |
| **Schema self-validation** | ✅ Complete | `tests/test_schemas.py`. | None. |
| **Semantic validation** | ✅ Complete | `scripts/validate_semantics.py`. | None. |
| **Skill structure / link check** | ✅ Complete | `scripts/check_skill.py`. | None. |
| **Release packaging validation** | ✅ Complete | `scripts/package_skill.py`, `scripts/check_release_contents.py`. | None. |
| **Shell invariant checker** | ❌ Missing | Workbench has `scripts/verify_invariants.sh`. | Not critical; Python validators cover invariants. |
| **Secret-scan CI with useful reporting** | 🟡 Partial | Step exists but reports no context on failure. | Fix `security-scan.yml`. |
| **Validation workflow installs dependencies** | ❌ Missing | `validate-skill.yml` runs `check_skill.py` without installing PyYAML. | Add `pip install -e ".[dev]"`. |
| **actionlint configuration** | ❌ Missing | Workbench has `.actionlint.yaml`. | Optional; can add if CI linting is adopted. |
| **pre-commit hooks** | ❌ Missing | Workbench has `.pre-commit-config.yaml`. | Optional for skill. |

---

## Documentation

| Workbench Capability | Skill Status | Missing / Gap | Action |
|----------------------|--------------|---------------|--------|
| **User guide** | ✅ Complete | `docs/USER_GUIDE.md` and `README.md`. | None. |
| **Developer guide** | ✅ Complete | `docs/DEVELOPER_GUIDE.md` and `CONTRIBUTING.md`. | Update with new validation commands. |
| **Architecture document** | ✅ Complete | `docs/ARCHITECTURE.md`. | Update if runtime changes. |
| **Security model / threat model** | ✅ Complete | `docs/SECURITY_MODEL.md`, `docs/THREAT_MODEL.md`. | None. |
| **Artifact format spec** | ❌ Missing | Workbench `docs/artifact-format.md` has concrete layout and JSON examples. | Create `docs/artifact-format.md`. |
| **Prompts audit** | ❌ Missing | Workbench `docs/PROMPTS_AUDIT.md`. | Optional; add if prompt library expands. |
| **Protocol archive (v3/v4)** | ❌ Missing | Workbench `protocol/archive/` holds historical versions. | Optional; skill has migration notes only. |
| **Provider/vendor integration guides** | ⚪ N/A | Application-specific. | Not appropriate for portable skill. |

---

## Repository Hygiene

| Workbench Capability | Skill Status | Missing / Gap | Action |
|----------------------|--------------|---------------|--------|
| **.gitignore for caches/build output** | ✅ Complete | Comprehensive `.gitignore`. | Add explicit `*.log`, `*.zip`, `development/generated/`, `development/audits/`. |
| **No committed __pycache__** | ✅ Complete | Ignored. | Clean local working tree. |
| **No committed .DS_Store** | ✅ Complete | Ignored. | Clean local working tree. |
| **Development-only boundary** | ✅ Complete | `development/` and `archive/` excluded from packaging. | None. |

---

## Summary

- **Complete (✅):** ~55 % of mapped capabilities.
- **Partial (🟡):** ~25 %.
- **Missing (❌):** ~15 %.
- **N/A (⚪):** ~5 %.

The biggest remaining deltas are:

1. Workflow playbook depth (security-audit and others).
2. Structured gate/methodology/prompt resource library.
3. Runtime health-score computation.
4. CI secret-scan reporting and dependency installation.
5. A consolidated artifact-format specification.

These are all addressable without rebuilding the Workbench application.
