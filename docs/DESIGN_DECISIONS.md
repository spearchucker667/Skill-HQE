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

## 5. ADR-005: Schema Metadata Reconciliation to v4.2.1
- **Status:** Accepted
- **Decision:** Update `$id` in `protocol/hqe-engineer-schema.json` from `...-v4.0.0.json` to `https://hqe.dev/schemas/hqe-engineer-v4.2.1.json` and title to `HQE Engineer Protocol v4.2.1 Schema`.
- **Rationale:**
  - Exhaustive search of both repositories confirmed no external software consumers or URI resolvers depend on the stale `v4.0.0` or `v4.2.0` string literals.
  - Eliminates schema validation warnings during strict semver audits while leaving structural validation rules identical.
