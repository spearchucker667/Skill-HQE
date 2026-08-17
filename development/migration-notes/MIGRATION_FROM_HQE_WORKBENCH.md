# Migration from HQE-Workbench to Skill-HQE (`/HQE`)

This document outlines the architectural migration and capability translation from the monolithic desktop application `HQE-Workbench` into the native agentic skill **Skill-HQE** (`/HQE`).

---

## 1. Architectural Differences

| Dimension | HQE-Workbench | Skill-HQE (`/HQE`) |
| :--- | :--- | :--- |
| **Architecture** | Tauri / Rust desktop application + React frontend | Native AI Agent Skill (`SKILL.md` + modular references + runtime layer) |
| **Execution Runtime** | Compiled native binary (`hqe` CLI / GUI) | Executed by agent host runtimes with Python deterministic runtime (`runtime/`) |
| **Protocol Authority** | `protocol/hqe-engineer.yaml` | `protocol/hqe-engineer.yaml` (canonical active v5.0.0 protocol source) |
| **Provider Orchestration** | `crates/hqe-openai/` custom client | Host AI agent's native reasoning & tool integration |
| **Persistence / Storage** | SQLite + SQLCipher encrypted database | Stateless / session artifacts (`HQE_SESSION_LOG.json`, `HQE_RUN_MANIFEST.json`) |
| **Secrets / Keyring** | System keychain integration | Ephemeral environment variables; strictly zero-leakage redaction |
| **Tooling & Helpers** | Native Rust crates (`hqe-core`, `hqe-artifacts`) | Lightweight standalone Python utilities (`scripts/*.py`) and `runtime/` engine |

---

## 2. What Was Ported (Direct Lineage)

1. **Active Protocol Control Plane (`protocol/hqe-engineer.yaml`)**:
   - The active v5.0.0 protocol is embedded directly in `protocol/`.
   - Execution ordering (Phase -1 through Phase 4) is enforced in `SKILL.md`.
   - Health score rubric (1–10 bands), severity gates, taint chains, and change budgets are active.
2. **Canonical Artifact Definitions**:
   - Risk Register, Master TODO Backlog, Pattern Findings, Quick Wins vs Structural Work, Security Posture Summary, Reliability Summary, Testing Gaps, Unknowns & Verification, and Confidence Declaration.
3. **Finding Taxonomy & ID Model**:
   - Standardized `HQE-<CAT>-<NUM>` prefixes (`BOOT`, `SEC`, `BUG`, `REL`, `PERF`, `UX`, `DX`, `DOC`, `DEBT`, `DEPS`).
4. **Secret Redaction Engine**:
   - Redaction patterns ported from `crates/hqe-core/src/redaction.rs` into `scripts/redact_secrets.py`.
5. **Local Static Risk Scanning**:
   - Heuristics ported from `crates/hqe-core/src/repo.rs` into `scripts/local_risk_scan.py`.

---

## 3. What Was Adapted (Methodological & Runtime Adaptation)

1. **Deterministic Execution & Runtime Layer**:
   - Ported core execution state, session management, evidence collection, and artifact pipeline into pure-Python `runtime/` modules (`runtime/session_manager.py`, `runtime/artifact_pipeline.py`, `runtime/finding_registry.py`, `runtime/evidence_store.py`, `runtime/run_manifest.py`).
2. **MCP Prompts & Reasoning Frameworks**:
   - Instead of running a background JSON-RPC MCP server (`mcp-server/`), prompt methodologies (5W1H, CAGEERF, FOCUS, REACT, SCAMPER) and quality gates were translated into `references/reasoning-methodologies.md` and `references/quality-gates.md`.
3. **Debugging & Trace Workflows**:
   - CLI debugging tools were adapted into actionable workflows: `workflows/debug-error.md` and `workflows/trace-regression.md`.
4. **Artifact Assembly**:
   - The Rust generation engine (`crates/hqe-artifacts/`) was translated into `runtime/artifact_pipeline.py`, Markdown templates (`templates/*.md`), and JSON schemas (`schemas/*.json`).

---

## 4. What Was Intentionally Dropped

1. **Desktop GUI**: Tauri configuration, React/TypeScript desktop frontend (`desktop/workbench/`).
2. **Keychain & SQLite Database**: `keyring` integration, local encrypted session databases (`crates/hqe-core/src/encrypted_db.rs`).
3. **Provider Network Adapters**: Raw OpenAI/Anthropic/Venice REST client wrappers (`crates/hqe-openai/`).
4. **MCP Transport Daemon**: JSON-RPC socket listeners and HTTP MCP transports.
5. **Historical Archive Protocols**: Obsolete v3.0.0 and v3.1.0 protocol YAMLs from the historical archive directory.
