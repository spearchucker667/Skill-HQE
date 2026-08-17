# HQE Source Audit & Licensing Provenance (v5.0.0)

This document records the exact source file lineage, checksums, modifications, and licensing boundaries for all components imported or adapted from [HQE-Workbench](/Users/super_user/Projects/HQE-Workbench) and the **HQE Protocol v5.0.0** package.

---

## 1. Source Lineage & Licensing Matrix

| Component | Source Path / Origin | Target Path in Skill-HQE | Declared Source License | Target License | Disposition & Notes |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Active Protocol YAML** | `protocol/hqe-engineer.yaml` | `protocol/hqe-engineer.yaml` | `MIT` (metadata) | `MIT` / `Apache-2.0` | Canonical v5.0.0 protocol source |
| **Active Protocol Schema** | `protocol/hqe-engineer-schema.json` | `protocol/hqe-engineer-schema.json` | `Apache-2.0` | `Apache-2.0` | JSON Schema Draft 2020-12 v5.0.0 |
| **Tooling Schema** | `protocol/hqe-schema.json` | `protocol/hqe-schema.json` | `Apache-2.0` | `Apache-2.0` | JSON Schema Draft 2020-12 v5.0.0 |
| **Protocol Validator** | `protocol/validate.py` | `protocol/validate.py` | `Apache-2.0` | `Apache-2.0` | Validates YAML vs Schema |
| **Protocol Verifier** | `protocol/verify.py` | `protocol/verify.py` | `Apache-2.0` | `Apache-2.0` | Standalone verbose verifier |
| **Redaction Engine** | `crates/hqe-core/src/redaction.rs` | `scripts/redact_secrets.py` | `Apache-2.0` | `Apache-2.0` | Translated to Python |
| **Local Risk Scanner** | `crates/hqe-core/src/repo.rs` | `scripts/local_risk_scan.py` | `Apache-2.0` | `Apache-2.0` | Translated to Python |
| **MCP Prompts & Gates** | `mcp-server/prompts/` | `references/quality-gates.md`, `references/reasoning-methodologies.md` | `Apache-2.0` | `Apache-2.0` | Translated to reference guides |
| **Root Repository** | `LICENSE` (root) | `LICENSE` (root) | `Apache-2.0` | `Apache-2.0` | Apache-2.0 governing framework |

---

## 2. Protocol v5.0.0 File Checksums (SHA-256)

```text
e0eaa19197edff2f1add367ba155a186a63ced10aa75d996b9abca6e37550d4a  hqe-engineer.yaml
facaaf1054a3a32ee5ae743f4db0bb5e3e9b8a34ee6f6a879aa2efd811462d43  hqe-engineer-schema.json
42b6d376322ae9b0b45ab39a7f83b332bac4a6943df5268dd45f92dd892078d1  hqe-schema.json
0b907bb2ac5994f8dae0030f7a20690c8ab745e872a78f452cdd5c8ed8fe788f  validate.py
3b70b677fcde2769e5e0c11120dc2ed7e04366c6cfb8c71ff17538872d1e3f89  verify.py
```

---

## 3. Protocol v5.0.0 Architecture Highlights

- **Schema Draft**: Fully upgraded to JSON Schema Draft 2020-12.
- **Control Plane Requirements**: Consolidated 1–10 health scoring, severity gates, likelihood/exposure justification, trust-boundary analysis, security taint tracking, change budgets ($\le 5$ files), anti-regression enforcement, stop-the-line incident handling, no-stall blocker instrumentation, and reproducibility manifests.
- **Finding Lifecycle**: Explicit lifecycle state tracking (`CONFIRMED`, `STRONGLY_SUPPORTED`, `SUSPECTED`, `NOT_REPRODUCED`, `FIXED`, `REOPENED`, `SUPERSEDED`).
- **Artifact Taxonomy**: Standardized metadata schema for all 9 canonical deliverables.
