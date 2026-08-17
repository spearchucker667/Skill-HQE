# HQE User Guide & Quickstart

Welcome to the **HQE Agent Skill** user guide. This document explains how to install, configure, and invoke HQE across various AI agent environments.

---

## 1. Supported Environments

HQE is compatible with any AI coding assistant or CLI environment that supports standard Agent Skills, markdown prompt injection, or slash commands:
- **Antigravity CLI** (`agy` / `gemini-cli`)
- **Kimi Code CLI** (`kimi`)
- **Claude Code** (`claude`)
- **Cursor IDE** & **Windsurf IDE**
- **Roo Code** / **Cline** / **Aider**

---

## 2. Installation & Setup

### Option A: Direct Skill Directory Inclusion
Copy or symlink the `Skill-HQE` directory into your agent's skills path:

```bash
# For Antigravity / Gemini CLI:
cp -r /path/to/Skill-HQE ~/.gemini/antigravity-cli/builtin/skills/hqe

# For Kimi Code / OMK:
cp -r /path/to/Skill-HQE ~/.agents/skills/hqe
```

### Option B: Local Repository Reference
Point your agent directly to this repository workspace or add it to your project-level `.agents/skills/` directory.

---

## 3. Invocation Commands & Modes

You can invoke HQE directly in your conversation with the agent using the `/HQE` slash command or natural language prompts:

### 3.1 Full Repository Audit
Perform an exhaustive health, security, and architecture review:
```text
/HQE audit
```
*Optional options: `--exhaustive`, `--quick`, `--deep`.*

### 3.2 Security Audit
Focus exclusively on attack surface, trust boundaries, credentials, and injections:
```text
/HQE security
```

### 3.3 Pull Request Review
Review uncommitted changes or a specific PR diff:
```text
/HQE pr-review
```

### 3.4 Targeted Bug Hunting
Deep dive on a specific subsystem, file, or bug symptom:
```text
/HQE targeted path/to/subsystem "Investigate race condition in cache eviction"
```

### 3.5 Safe Remediation
Implement minimal-change, verified root-cause fixes for identified findings:
```text
/HQE remediate --findings=HQE_FINDINGS.json
```

### 3.6 Agent Handoff Generation
Generate a structured, implementation-ready handoff document for another agent:
```text
/HQE handoff
```

---

## 4. Understanding Audit Artifacts

An `/HQE audit` produces two standard artifacts:
1. **`HQE_REPORT.md`**: Human-readable executive summary, coverage ledger, categorized findings, and remediation roadmap.
2. **`HQE_FINDINGS.json`**: Machine-readable array of findings validated against `schemas/findings.schema.json`.

---

## 5. CLI Helper Tools

HQE includes standalone Python tools in `scripts/`:

```bash
# 1. Inventory repository files and compute statistics
python3 scripts/inventory_repo.py /path/to/repo

# 2. Validate findings JSON against the official schema
python3 scripts/validate_findings.py findings.json

# 3. Check the internal integrity of the HQE skill itself
python3 scripts/check_skill.py .
```
