# Privacy Policy & Data Handling Specification

**Last Updated**: 2026-08-17  
**Status**: Authoritative

The **HQE Agent Skill** (`/HQE`) is architected with a **Local-First, Zero-Telemetry, Privacy-Preserving** philosophy. This document clarifies data processing, transmission, and retention characteristics when utilizing the HQE skill across any AI runtime environment.

---

## 1. Zero External Telemetry
- **No Phone-Home Logic**: The HQE skill contains **zero** tracking pixels, telemetry beacons, external metrics reporting, or analytics pings.
- **No Cloud Services**: The skill does not connect to any proprietary HQE cloud services. All scripts (`inventory_repo.py`, `validate_findings.py`, `check_skill.py`) execute locally on the host machine.

## 2. Repository Data & Ingestion Boundary
When an agent executes an `/HQE` audit or review:
- **Local File Access**: File inspection is mediated strictly by your AI agent host runtime's file viewing tools.
- **Redaction of Secrets**: In accordance with [references/security-review.md](references/security-review.md) and [references/prompt-injection-defense.md](references/prompt-injection-defense.md), any API keys, credentials, tokens, or sensitive certificates detected during audits must be replaced with `[REDACTED]` in all findings, reports, logs, and run manifests.
- **Ephemeral Scratch Storage**: Temporary files and cache directories created by helper scripts are placed within standard git-ignored directories (`.tmp`, `__pycache__`) and contain no persistent external references.

## 3. Host AI Runtime & Model Provider Data Flows
The HQE skill consists of structured Markdown instructions, JSON schemas, and local Python scripts. Data sent to third-party LLM providers (e.g., OpenAI, Anthropic, Google, local Ollama/vLLM instances) is governed exclusively by:
1. The **API Terms of Service** and **Privacy Policy** of the model provider configured in your host AI tool.
2. Your specific agent client settings (e.g., zero-data-retention agreements for enterprise API tiers).

## 4. Compliance & Enterprise Security
- **Air-Gapped Operation**: The entire HQE skill is fully functional in completely air-gapped, offline environments using local models and offline toolchains.
- **SOC 2 & ISO 27001 Alignment**: By ensuring deterministic output structures, mandatory redacting of detected credentials, and preventing unauthorized outbound network calls, HQE is suitable for integration into compliance-sensitive development lifecycles.

---
*For questions regarding privacy practices, consult [SECURITY.md](SECURITY.md) or open an issue on the repository.*
