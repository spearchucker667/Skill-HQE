# Skill-HQE Architectural Design Decisions

This document records the architectural decisions, trade-offs, and rationale guiding the design of **Skill-HQE**.

---

## 1. ADR-001: Direct Embedding of Canonical Protocol YAML
- **Status:** Accepted
- **Decision:** Embed `protocol/hqe-engineer.yaml` as the machine-readable ground truth within `protocol/`, rather than transpiling it into generic markdown or a massive static system prompt.
- **Rationale:**
  - Establishes a verifiable contract between source methodology and runtime execution.
  - Allows deterministic validation via `protocol/validate.py` and `scripts/validate_protocol_bundle.py`.
  - Enables progressive disclosure: runtime agents read compact rules in `SKILL.md` and only query specific protocol sections when resolving ambiguities.

---

## 2. ADR-002: Progressive Disclosure Model
- **Status:** Accepted
- **Decision:** Keep `SKILL.md` under 150 lines, serving as a routing and constraint hub, and delegate domain specifics to targeted documents in `references/` and `workflows/`.
- **Rationale:**
  - Prevents context window exhaustion on routine agent invocations.
  - Improves instruction adherence by focusing the model's attention only on the active operating mode.

---

## 3. ADR-003: Standalone Lightweight Python Tooling
- **Status:** Accepted
- **Decision:** Implement helper utilities (`inventory_repo.py`, `detect_manifests.py`, `local_risk_scan.py`, `redact_secrets.py`) as standalone Python 3 scripts with zero mandatory external runtime dependencies for basic operation.
- **Rationale:**
  - Python is universally available across developer machines, CI runners, and agent sandboxes.
  - Avoids requiring a Rust toolchain or native compilation just to inventory a repository or check manifest files.

---

## 4. ADR-004: Fail-Closed Schema Validation
- **Status:** Accepted
- **Decision:** Schema validation tools (`validate_findings.py`, `validate_manifest.py`, `validate_session_log.py`) fail closed with clear error messages if `jsonschema` is unavailable, rather than silently falling back to no-op "basic checks".
- **Rationale:**
  - Machine-readable artifacts must strictly conform to schema specifications to maintain cross-agent reliability.
  - Prevents false-positive audit passes in CI pipelines.

---

## 5. ADR-005: Schema Metadata Reconciliation
- **Status:** Superseded by ADR-006
- **Decision:** Updated schema metadata to align with active protocol versions.

---

## 6. ADR-006: Protocol v5.0.0 Upgrade & Deterministic Python Runtime Layer
- **Status:** Accepted
- **Decision:** Upgrade canonical protocol to **HQE Engineer Protocol v5.0.0** (JSON Schema Draft 2020-12) and implement a pure-Python deterministic control-plane runtime layer (`runtime/` package) comprising `session_manager.py`, `finding_registry.py`, `evidence_store.py`, `run_manifest.py`, and `artifact_pipeline.py`.
- **Rationale:**
  - Standardizes the 1–10 health scoring system, severity gates, taint chains, change budget (<=5 files), anti-regression rules, stop-the-line incident handling, and no-stall blocker instrumentation.
  - Replaces instructional-only agent guidance with deterministic, verifiable state machines for finding lifecycles, session persistence, evidence collection, and automated assembly of all 9 canonical audit deliverables.
  - Preserves 100% host portability without compiling Rust binaries while enforcing control-plane behavior.

