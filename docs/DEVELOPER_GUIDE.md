# HQE Developer & Extension Guide

This guide is for developers and contributors extending the **HQE Agent Skill** with new language guides, diagnostic schemas, workflows, or validation scripts.

---

## 1. Adding a New Language Guide

Language guides live in `references/language-guides/<language>.md`. When creating a new language guide:
1. **Manifests & Project Layout**: Specify package managers, configuration files, and standard project layouts.
2. **Build & Test Idioms**: Document canonical test runners, lint commands, and typecheckers.
3. **Common Bug Patterns**: List memory safety pitfalls, concurrency bugs, async/await anti-patterns, nil/null pointer risks, and resource leak risks specific to the ecosystem.
4. **Security Checkpoints**: Document ecosystem-specific injection vectors (e.g., prototype pollution in JS, unsafe blocks in Rust, deserialization in Python/Java).

---

## 2. Extending Finding & Manifest Schemas

All schemas reside in `schemas/` and must adhere to **JSON Schema Draft-07**.

### Schema Extension Checklist:
1. Edit the schema in `schemas/`.
2. Update corresponding sample fixtures in `tests/fixtures/`.
3. Run `python3 -m unittest tests/test_skill_suite.py` to confirm zero regressions.
4. Update `templates/` to reflect any new mandatory properties in markdown outputs.
5. Update `docs/FINDING_SPECIFICATION.md`.

---

## 3. Developing New Workflows

Workflows in `workflows/` define the phased reasoning procedure for specific audit modes.
Every workflow must include:
- **Prerequisites & Context Ingestion**
- **Step-by-Step Phased Execution**
- **Evidence Gathering Requirements**
- **Output Artifact Generation Specification**
