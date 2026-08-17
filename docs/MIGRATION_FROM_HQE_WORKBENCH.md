# Migration from HQE-Workbench to Skill-HQE (`/HQE`)

This document outlines the architectural migration and capability translation from the monolithic desktop application [HQE-Workbench](https://github.com/hqe-project/hqe-workbench) (`/Users/super_user/Projects/HQE-Workbench`) into the native agentic skill **Skill-HQE** (`/Users/super_user/Projects/Skill-HQE`).

---

## 1. Architectural Differences

| Dimension | HQE-Workbench | Skill-HQE (`/HQE`) |
| :--- | :--- | :--- |
| **Architecture** | Tauri / Rust desktop application + React frontend | Native AI Agent Skill (`SKILL.md` + modular references/workflows) |
| **Execution Runtime** | Compiled native binary (`hqe` CLI / GUI) | Executed by agent host runtimes (Gemini CLI, Antigravity, Claude) |
| **Protocol Authority** | `protocol/hqe-engineer.yaml` | `protocol/hqe-engineer.yaml` (embedded byte-for-byte active source) |
| **Provider Orchestration** | `crates/hqe-openai/` custom client | Host AI agent's native reasoning & tool integration |
| **Persistence / Storage** | SQLite + SQLCipher encrypted database | Stateless / session artifacts (`HQE_SESSION_LOG.json`, `HQE_RUN_MANIFEST.json`) |
| **Secrets / Keyring** | System keychain integration | Ephemeral environment variables; strictly zero-leakage redaction |
| **Tooling & Helpers** | Native Rust crates (`hqe-core`, `hqe-artifacts`) | Lightweight standalone Python utilities (`scripts/*.py`) |

---

## 2. What Was Ported (Direct Lineage)

1. **Active Protocol Control Plane (`protocol/hqe-engineer.yaml`)**:
   - The active v4.2.1 protocol is embedded directly in `protocol/`.
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

## 3. What Was Translated (Methodological Adaptation)

1. **MCP Prompts & Reasoning Frameworks**:
   - Instead of running a background JSON-RPC MCP server (`mcp-server/`), the high-value prompt methodologies (5W1H, CAGEERF, FOCUS, REACT, SCAMPER) and quality gates were translated into `references/reasoning-methodologies.md` and `references/quality-gates.md`.
2. **Debugging & Trace Workflows**:
   - CLI debugging tools were adapted into actionable workflows: `workflows/debug-error.md` and `workflows/trace-regression.md`.
3. **Artifact Generation**:
   - The Rust generation engine (`crates/hqe-artifacts/`) was translated into Markdown templates (`templates/*.md`) and JSON schemas (`schemas/*.json`).

---

## 4. What Was Intentionally Dropped

1. **Desktop GUI**: Tauri configuration, React/TypeScript desktop frontend (`desktop/workbench/`).
2. **Keychain & SQLite Database**: `keyring` integration, local encrypted session databases (`crates/hqe-core/src/encrypted_db.rs`).
3. **Provider Network Adapters**: Raw OpenAI/Anthropic/Venice REST client wrappers (`crates/hqe-openai/`).
4. **MCP Transport Daemon**: JSON-RPC socket listeners and HTTP MCP transports.
5. **Historical Archive Protocols**: Obsolete v3.0.0 and v3.1.0 protocol YAMLs from the historical archive directory.
