# HQE Developer & Extension Guide

**Skill Version**: 5.0.0 (`VERSION`)  
**Protocol Version**: HQE Engineer Protocol v5.0.0 (`protocol/hqe-engineer.yaml`)  
**Target Audience**: Developers, Protocol Engineers, AI Agent Maintainers

---

## 1. Architectural Philosophy & Layer Hierarchy

The **Skill-HQE** repository is designed as a strict layered system that bridges machine-readable protocol authority, agent operational contracts, deterministic execution runtime, and developer tooling:

```text
Canonical Protocol Authority (protocol/hqe-engineer.yaml)
                       ↓
Agent Operational Projection (SKILL.md)
                       ↓
Modular Domain References (references/)
                       ↓
Procedural Workflows (workflows/)
                       ↓
Artifact Templates (templates/) & JSON Schemas (schemas/)
                       ↓
Deterministic Runtime Engine (runtime/)
                       ↓
Standalone Helper Tooling (scripts/) & Validation Suites (tests/)
```

### Layer Rules:
1. **Protocol Immutability**: `protocol/hqe-engineer.yaml` is the canonical machine-readable ground truth. Do not edit protocol YAML without reviewing schema, validators, and checksums.
2. **Compact Skill Entrypoint**: `SKILL.md` is an operational routing hub. It must remain under 150 lines and leverage **progressive disclosure** by pointing to `references/` and `workflows/`.
3. **Deterministic Control Plane**: Logic that can be validated programmatically (finding lifecycles, evidence triads, secret redaction, deliverable assembly) is executed via the `runtime/` engine rather than relying solely on LLM compliance.
4. **Zero-Debris Packaging**: Release packages must never contain cache artifacts, `.DS_Store`, or git metadata.

---

## 2. The Deterministic Python Runtime Layer (`runtime/`)

The `runtime/` package provides a pure-Python, zero-dependency control plane that mirrors the state machine and artifact generation capabilities of the reference implementation:

### 2.1 `session_manager.py` (Session State Machine)
Tracks execution lifecycles across agent turns:
- **States**: `INITIALIZED` → `ORIENTING` → `ANALYZING` → `REMEDIATING` → `VERIFYING` → `FINALIZING` → `COMPLETED` (or `STOP_THE_LINE` upon critical security incident).
- Enforces valid state transitions and exports `HQE_SESSION_LOG.json`.

```python
from runtime import SessionManager, SessionState

sm = SessionManager(repo_path="/path/to/repo")
sm.transition(SessionState.ORIENTING, "Phase 0 repository discovery")
sm.record_command("pytest -v", exit_code=0)
sm.save_session_log("HQE_SESSION_LOG.json")
```

### 2.2 `finding_registry.py` (Finding State Machine & Severity Gates)
Maintains finding invariants and lifecycle transitions:
- **Lifecycle States**: `CONFIRMED`, `STRONGLY_SUPPORTED`, `SUSPECTED`, `NOT_REPRODUCED`, `FIXED`, `REOPENED`, `SUPERSEDED`.
- **Severity Gating**: Rejects `CRITICAL` or `HIGH` findings if `preconditions`, `exploitability`, `blast_radius`, `likelihood`, or `exposure_evidence` are missing.

```python
from runtime import FindingRegistry, FindingLifecycle

registry = FindingRegistry()
finding = registry.register({
    "id": "HQE-SEC-001",
    "category": "SEC",
    "severity": "HIGH",
    "confidence": "FACT",
    "status": "CONFIRMED",
    "title": "Hardcoded Secret Fallback",
    "affected_component": "src/auth.py",
    "preconditions": ["ENV unset"],
    "exploitability": "Trivial signature forgery",
    "blast_radius": "All active user sessions",
    "likelihood": "High",
    "exposure_evidence": "auth.py#L42 exposed to HTTP listener",
    "evidence": [{"path": "src/auth.py", "start_line": 42, "end_line": 45, "snippet": "secret = 'dev'"}]
})
```

### 2.3 `evidence_store.py` (Code Evidence Triads & Secret Redactor)
- Validates that code evidence contains all required components: `path`, line range (`start_line`/`end_line`) or `anchor`, and a 2–5 line `snippet`.
- Automatically executes regex-based deterministic secret redaction.

### 2.4 `run_manifest.py` (Run Manifest Generator)
Generates structured `HQE_RUN_MANIFEST.json` capturing git commit hash, repository dirty status, tool executions, files reviewed, and finding counts.

### 2.5 `artifact_pipeline.py` (Canonical Deliverable Assembly)
Assembles all 9 canonical markdown deliverables from registered findings and verification results:
```python
from runtime import ArtifactPipeline

pipeline = ArtifactPipeline(findings=registry.all_findings(), session=sm.to_dict())
deliverables = pipeline.build_all_deliverables()
pipeline.write_to_directory("./audit-output")
```

---

## 3. Developing & Adding Workflows

Workflows reside in `workflows/<workflow-name>.md` and define step-by-step reasoning procedures for agent execution.

### Workflow Template Checklist:
1. **Header & Mode**: Declare workflow title, objective, and mode routing.
2. **Prerequisites**: Specify required context (e.g., Phase 0 orientation completed, git status clean).
3. **Phased Procedural Steps**: Detail step-by-step diagnostic or remediation procedures.
4. **Evidence Requirements**: Specify mandatory evidence gathering (file paths, snippets, verification commands).
5. **Output Deliverables**: List expected markdown reports and JSON artifacts.
6. **Registration**: Add the workflow to `SKILL.md` under Operating Modes, `scripts/check_skill.py`, and `tests/test_workflow_contracts.py`.

---

## 4. Developing & Extending References and Language Guides

### 4.1 Modular References (`references/`)
Reference guides provide domain-specific methodologies (security, reliability, performance, architecture, testing).
- Must adhere to **evidence-first principles**.
- Must use lowercase hyphenated filenames (e.g., `references/security-review.md`).
- Must not duplicate `SKILL.md` operational rules.

### 4.2 Language Diagnostic Guides (`references/language-guides/`)
Add language-specific diagnostics under `references/language-guides/<language>.md`:
1. **Manifests & Layouts**: Common package managers and directory layouts.
2. **Build & Verification Commands**: Canonical compile, test, and typecheck commands.
3. **Common Bug Patterns**: Memory safety pitfalls, concurrency bugs, async/await anti-patterns, null pointers.
4. **Security Checkpoints**: Ecosystem-specific vulnerabilities (e.g., prototype pollution in JS/TS, unsafe blocks in Rust, deserialization in Python/Java).

---

## 5. Extending Schemas & Templates

All machine-readable schemas reside in `schemas/` and must adhere to **JSON Schema Draft-07**:

1. Edit schema in `schemas/<name>.schema.json`.
2. Update corresponding sample fixtures in `tests/fixtures/`.
3. Update corresponding markdown template in `templates/<name>.md`.
4. Run `pytest tests/test_schemas.py` and `pytest tests/test_template_contracts.py`.
5. Update `docs/FINDING_SPECIFICATION.md` if finding schemas change.

---

## 6. Developing Helper Scripts (`scripts/`)

All scripts in `scripts/` must adhere to these standards:
- **Portability**: Standard Python 3.10+ with zero mandatory third-party runtime dependencies for base operation.
- **CLI Interface**: Standard `argparse` with `--help` documentation and sensible defaults.
- **Clean Exit Codes**: `0` on success, non-zero on validation error or failure.
- **Safe Execution**: Read-only by default; never modify files without explicit flags.

---

## 7. Running the Validation & Test Suite

Before committing any changes, run the full validation suite:

```bash
# 1. Compile all Python scripts, tests, and runtime modules
python3 -m compileall -q scripts tests runtime

# 2. Run complete pytest test suite (66+ tests)
pytest -v

# 3. Validate protocol YAML against schema
python3 protocol/validate.py protocol/hqe-engineer.yaml
python3 protocol/validate.py --schema

# 4. Strict protocol bundle validation
python3 scripts/validate_protocol_bundle.py --strict-schema-metadata

# 5. Check protocol SHA-256 integrity and synchronization
python3 scripts/check_protocol_sync.py .

# 6. Check skill structural integrity, schema validity, and markdown links
python3 scripts/check_skill.py .

# 7. Check release allowlist conformance
python3 scripts/check_release_contents.py .
```

---

## 8. Repository Boundaries & Release Packaging

Skill-HQE enforces a clean separation across three distinct repository zones:

### 8.1 Repository Zones
1. **Runtime Skill Files**: Required by AI agents executing `/HQE` (`SKILL.md`, `protocol/`, `references/`, `workflows/`, `templates/`, `schemas/`, `runtime/`, `scripts/`, `docs/`, `LICENSE`, `NOTICE`, `VERSION`, `CHANGELOG.md`).
2. **Development & Maintenance Workspace (`development/`)**: Maintainer-only assets (`audits/`, `agent-handoffs/`, `investigations/`, `migration-notes/`, `design-notes/`, `benchmarks/`, `experiments/`, `generated/`). Never included in release packages.
3. **Historical Archive (`archive/`)**: Obsolete revisions and historical assets retained for provenance (`historical/`, `deprecated/`, `old-releases/`). Never loaded by runtime routines.

### 8.2 Building & Verifying a Release Bundle

```bash
# 1. Package clean release bundle (automatically invokes check_release_contents.py):
python3 scripts/package_skill.py --source . --output /tmp/Skill-HQE-v5.0.0.zip

# 2. Verify release archive contents against allowlist:
python3 scripts/check_release_contents.py /tmp/Skill-HQE-v5.0.0.zip

# 3. Test clean installation extraction:
mkdir -p /tmp/hqe-clean-test
unzip /tmp/Skill-HQE-v5.0.0.zip -d /tmp/hqe-clean-test
python3 scripts/check_release_contents.py /tmp/hqe-clean-test/Skill-HQE
```

