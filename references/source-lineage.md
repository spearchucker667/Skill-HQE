# Source Lineage & Licensing Provenance

**Protocol Authority**: HQE Engineer Protocol v5.0.0 (`protocol/hqe-engineer.yaml`)  
**License**: Apache-2.0 (Framework and Protocol Metadata)

---

## 1. Provenance Overview

The **Skill-HQE** repository is an agentic, portable conversion of the engineering methodology originally developed in **HQE-Workbench**.

While `HQE-Workbench` implemented this methodology as a monolithic Tauri/Rust desktop application, `Skill-HQE` extracts and standardizes the core engineering protocols, schemas, workflows, and reasoning playbooks into an agent-native skill.

---

## 2. Component Lineage Mapping

| Skill-HQE Component | Origin in HQE-Workbench | License | Notes |
| :--- | :--- | :--- | :--- |
| `protocol/hqe-engineer.yaml` | `protocol/hqe-engineer.yaml` | Apache-2.0 | Canonical machine-readable protocol definition (v5.0.0) |
| `protocol/hqe-engineer-schema.json` | `protocol/hqe-engineer-schema.json` | Apache-2.0 | JSON Schema Draft 2020-12 validator contract |
| `protocol/validate.py` | `protocol/validate.py` | Apache-2.0 | Canonical protocol validation script |
| `protocol/verify.py` | `protocol/verify.py` | Apache-2.0 | Standalone verbose protocol verifier |
| `scripts/redact_secrets.py` | `crates/hqe-core/src/redaction.rs` | Apache-2.0 | Ported regex secret redaction patterns to Python 3.10+ |
| `scripts/local_risk_scan.py` | `crates/hqe-core/src/repo.rs` | Apache-2.0 | Ported static risk detection rules to Python 3.10+ |
| `scripts/inventory_repo.py` | `crates/hqe-core/src/repo.rs` | Apache-2.0 | Ported file traversal and classification logic |
| `runtime/` | `crates/hqe-core/`, `crates/hqe-artifacts/` | Apache-2.0 | Re-implemented state machines and artifact builder in pure Python |
| `references/reasoning-methodologies.md` | `mcp-server/prompts/` | Apache-2.0 | Translated 5W1H, CAGEERF, FOCUS, REACT, SCAMPER prompts |
| `references/quality-gates.md` | `mcp-server/prompts/server/resources/gates/` | Apache-2.0 | Translated quality evaluation gates (summary form) |
| `references/gates/` | `mcp-server/prompts/server/resources/gates/` | Apache-2.0 | Per-gate reference documents with activation and retry guidance |
| `references/methodologies/` | `mcp-server/prompts/server/resources/methodologies/` | Apache-2.0 | Per-methodology reference documents (5W1H, CAGEERF, FOCUS, ReACT, SCAMPER) |
| `references/methodologies/styles.md` | `mcp-server/prompts/server/resources/styles/` | Apache-2.0 | Translated response style guidance (analytical, creative, procedural, reasoning) |
| `references/language-guides/` | `mcp-server/prompts/` | Apache-2.0 | Translated language-specific review guides (9 ecosystems) |

---

## 3. Cryptographic Checksums (SHA-256)

Canonical protocol assets are pinned and validated via `protocol/SOURCE_CHECKSUMS.sha256`:

```text
e0eaa19197edff2f1add367ba155a186a63ced10aa75d996b9abca6e37550d4a  protocol/hqe-engineer.yaml
facaaf1054a3a32ee5ae743f4db0bb5e3e9b8a34ee6f6a879aa2efd811462d43  protocol/hqe-engineer-schema.json
36e7eddef90b038025e4f9c5f9ad5db908991a710a2f47a759903f2348e53389  protocol/hqe-schema.json
0b907bb2ac5994f8dae0030f7a20690c8ab745e872a78f452cdd5c8ed8fe788f  protocol/validate.py
71d2f175e16e88638f72cf8f2f097345620d03e1ed386eb0c00ca3d8b956e702  protocol/verify.py
```

---

## 4. Third-Party Code & Dependency Isolation

1. **Zero External Runtime Dependencies**: All helper scripts in `scripts/` and runtime modules in `runtime/` operate using standard library Python.
2. **Untrusted Codebase Separation**: Code inspected during `/HQE` execution is treated as untrusted data and is never executed directly by the skill framework without explicit user instruction.
3. **Attribution & Copyright**: All original copyright notices from HQE-Workbench are preserved in [`NOTICE`](../NOTICE).
