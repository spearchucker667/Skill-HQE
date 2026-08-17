# Privacy Policy & Data Handling Specification

**Last Updated**: 2026-08-17  
**Status**: Authoritative

The **HQE Agent Skill** (`/HQE`) is architected with a **Local-First, Zero-Telemetry, Privacy-Preserving** philosophy. This document clarifies data processing, transmission, and retention characteristics when utilizing the HQE skill across any AI runtime environment.

---

## 1. Local Operation
- **Skill Execution**: The HQE skill is a set of instructions, schemas, and helper scripts designed to run locally within your AI agent's execution environment.
- **Agent Reliance**: The skill relies entirely on the host AI agent for file access, context management, and execution sandboxing.

## 2. Data Flow & Security
- **Data Transmission**: The skill itself does not transmit data. Any data sent to third-party LLM providers is governed exclusively by your host agent's configuration and the API Terms of Service of your chosen provider.
- **Secret Handling**: While the skill instructs the agent to redact discovered secrets, this process is heuristic and dependent on the agent's capabilities. Users must not rely on the skill for guaranteed secret prevention or data loss prevention.
- **Sandboxing**: The skill does not provide containerization or sandboxing. It assumes the host AI agent operates within a safely isolated environment.

---
*For questions regarding privacy practices, consult [SECURITY.md](SECURITY.md) or open an issue on the repository.*
