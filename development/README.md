# Skill-HQE Development & Maintenance Workspace

This directory contains internal engineering audits, historical agent handoff notes, migration assessments, benchmark records, and experimental scratchpads used during the development and maintenance of **Skill-HQE**.

> [!IMPORTANT]
> Files in `development/` are **maintenance-only assets**. They are strictly excluded from runtime distribution packages (`scripts/package_skill.py`) and are not loaded by AI agents executing `/HQE`.

---

## Directory Taxonomy

| Subdirectory | Purpose |
| :--- | :--- |
| [`audits/`](audits/) | Completed repository health audits, hygiene reports, and verification logs. |
| [`agent-handoffs/`](agent-handoffs/) | Historical agent prompt handoffs and multi-session continuation records. |
| [`investigations/`](investigations/) | Deep-dive research notes, spike investigations, and architectural analyses. |
| [`migration-notes/`](migration-notes/) | Historical capability mappings and migration records from HQE-Workbench. |
| [`design-notes/`](design-notes/) | Draft design proposals and architectural sketches preceding formal ADRs. |
| [`benchmarks/`](benchmarks/) | Performance benchmarks, token economy metrics, and latency logs. |
| [`experiments/`](experiments/) | Experimental prompt formulations, alternative schemas, and prototype scripts. |
| [`generated/`](generated/) | Temporary generated artifacts, test outputs, and validation dumps. |
