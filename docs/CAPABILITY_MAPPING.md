# HQE Capability Mapping

This document details the disposition of capabilities extracted from the HQE-Workbench repository during its conversion to the `/HQE` agent skill.

## Core Capabilities

### Evidence-first Finding Model
- **Source files**: `protocol/hqe-engineer.yaml`, `protocol/hqe-schema.json`
- **Disposition**: PORT
- **Target skill component**: `SKILL.md`, `schemas/finding.schema.json`
- **Reason**: This is the core intellectual property and methodology of HQE. It must form the foundation of the agent skill.
- **Validation**: Schema validation and acceptance testing.

### Severity/Confidence/Effort Tiers
- **Source files**: `protocol/hqe-engineer.yaml`
- **Disposition**: PORT
- **Target skill component**: `references/severity-confidence-effort.md`, `schemas/finding.schema.json`
- **Reason**: Standardizing risk and effort is essential for prioritization and remediation planning.
- **Validation**: Schema validation and acceptance testing.

### Finding ID Structure
- **Source files**: `protocol/hqe-engineer.yaml`
- **Disposition**: PORT
- **Target skill component**: `SKILL.md`, `schemas/finding.schema.json`
- **Reason**: Stable finding IDs are critical for tracking issues across sessions and deduplication.
- **Validation**: Schema validation.

### Secret Handling & Redaction
- **Source files**: `crates/hqe-core/src/redaction.rs`, `docs/SECURITY_MODEL.md`
- **Disposition**: TRANSLATE
- **Target skill component**: `references/security-review.md`, `SKILL.md` (Do-not rules)
- **Reason**: As an agent skill, it shouldn't natively implement a regex engine for redaction within its core logic, but it MUST follow the strict rule of never exposing secrets or leaking credentials.
- **Validation**: Acceptance testing on repository with mock secrets.

### Repository Scanning and Ingestion
- **Source files**: `crates/hqe-core/src/repo.rs`, `crates/hqe-ingest/`
- **Disposition**: TRANSLATE
- **Target skill component**: `scripts/inventory_repo.py`, `references/large-repo-strategy.md`, `references/repository-orientation.md`
- **Reason**: The Rust ingestion engine is not portable to a pure agent skill, but the *methodology* of scanning safely and respecting ignores must be translated into helper scripts and agent instructions.
- **Validation**: Script execution on a sample repository.

### Audit Artifacts (Report, Manifest)
- **Source files**: `crates/hqe-artifacts/`
- **Disposition**: TRANSLATE
- **Target skill component**: `templates/report.md`, `templates/run-manifest.md`, `schemas/run-manifest.schema.json`
- **Reason**: The artifacts represent the deliverables. The Rust generation code is dropped, but the artifact structure and schema are ported.
- **Validation**: Schema validation.

### Git and Patch Workflows
- **Source files**: `crates/hqe-git/`, `cli/hqe/src/main.rs`
- **Disposition**: TRANSLATE
- **Target skill component**: `SKILL.md`, `workflows/remediation-run.md`, `workflows/pr-review.md`
- **Reason**: The agent environment already has tools to read diffs and apply patches. We port the rules on *how* to use them safely (e.g., check `git status`, protect working tree).
- **Validation**: Acceptance testing for remediation.

### Provider/LLM Integration
- **Source files**: `crates/hqe-openai/`
- **Disposition**: DROP
- **Target skill component**: None
- **Reason**: Provider client orchestration is the responsibility of the host agent runtime, not the skill.
- **Validation**: N/A

### Encrypted Chat Persistence & Keys
- **Source files**: `crates/hqe-core/src/encrypted_db.rs`, `keyring` usage
- **Disposition**: DROP
- **Target skill component**: None
- **Reason**: Application session persistence and keychain integration are host/application concerns, not skill capabilities.
- **Validation**: N/A

### Desktop Application UI
- **Source files**: `desktop/workbench/`, Tauri config
- **Disposition**: DROP
- **Target skill component**: None
- **Reason**: UI is explicitly excluded from the agent skill.
- **Validation**: N/A

### MCP Server & Prompt Library
- **Source files**: `mcp-server/`, `crates/hqe-mcp/`
- **Disposition**: TRANSLATE
- **Target skill component**: `workflows/*.md`, `references/*.md`
- **Reason**: The prompts and reasoning models are extremely valuable. They are translated into Markdown reference guides and workflows instead of a dedicated MCP server.
- **Validation**: Review of translated workflows.

### Protocol Schemas & Validators
- **Source files**: `protocol/`, `scripts/validate_protocol.sh`
- **Disposition**: TRANSLATE
- **Target skill component**: `schemas/*.json`, `scripts/validate_findings.py`, `scripts/check_skill.py`
- **Reason**: Schema validation is crucial. The Python validators are adapted to validate the specific artifacts produced by the skill.
- **Validation**: Running the validation scripts against fixtures.
