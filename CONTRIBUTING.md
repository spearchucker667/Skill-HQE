# Contributing to the HQE Agent Skill

Thank you for your interest in contributing to the **HQE Agent Skill**! We welcome contributions that refine our auditing methodology, expand language-specific diagnostic guides, strengthen prompt-injection defenses, and improve automated validation.

---

## 1. Development Principles
When contributing to HQE, preserve the core engineering philosophy:
1. **Evidence-First**: Every diagnostic rule must emphasize verifiable proof over speculation.
2. **Minimal-Change Bias**: Tooling and workflows must advocate for the smallest coherent fix.
3. **Structured & Machine-Readable**: All findings and artifacts must strictly adhere to JSON Schemas.
4. **Platform-Agnostic**: Keep workflows and scripts compatible across all major AI agent runtimes (Antigravity CLI, Kimi Code, Claude Code, Cursor, Roo Code, etc.).

---

## 2. Repository Layout & Conventions
- `SKILL.md`: Main entrypoint and high-level routing for AI agents. Keep concise; use progressive disclosure.
- `schemas/`: Draft-07 JSON Schemas (`finding.schema.json`, `findings.schema.json`, `run-manifest.schema.json`, `handoff.schema.json`).
- `runtime/`: Deterministic Python execution runtime (`session_manager.py`, `finding_registry.py`, `evidence_store.py`, `run_manifest.py`, `artifact_pipeline.py`).
- `references/`: Topic-specific deep dives loaded conditionally by agents.
- `references/language-guides/`: Language-specific idioms, static analysis tools, and bug patterns (9 languages).
- `workflows/`: Step-by-step procedural playbooks for audit modes (`full-audit.md`, `pr-review.md`, etc.).
- `templates/`: Markdown templates for canonical deliverables, findings, and handoffs.
- `schemas/`: Draft-07 JSON Schemas (`finding.schema.json`, `run-manifest.schema.json`, `session-log.schema.json`, etc.).
- `scripts/`: Local Python 3.10+ utilities with minimal external dependencies.
- `tests/`: Automated pytest unit, semantic, contract, and acceptance test suites.

---

## 3. Local Development & Verification
Before submitting a Pull Request, run the local verification suite:

```bash
# 1. Compile all Python scripts, tests, and runtime modules
python3 -m compileall -q scripts tests runtime

# 2. Run the pytest test suite
pytest -v

# 3. Verify skill structural completeness & links
python3 scripts/check_skill.py .

# 4. Verify protocol sync & schema integrity
python3 scripts/check_protocol_sync.py .
python3 scripts/validate_protocol_bundle.py --strict-schema-metadata
```

---

## 4. Pull Request Guidelines
- **Atomic Commits**: Use Conventional Commits (`feat:`, `fix:`, `docs:`, `test:`, `refactor:`).
- **Schema Changes**: If you modify any JSON schema in `schemas/`, ensure all test fixtures in `tests/fixtures/` and scripts in `scripts/` are updated and validated.
- **Documentation**: Any new workflow or reference must be documented in `SKILL.md` and linked in `README.md`.
- **No Unused Code / Dead Files**: Keep the repository lean, fast, and token-efficient for AI ingestion.

---

## 5. Security & Bug Reports
For security vulnerabilities, please do not open public issues. Follow the confidential disclosure policy in [SECURITY.md](SECURITY.md).
