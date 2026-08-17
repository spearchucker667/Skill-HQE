<div align="center">

```
  _    _  ____  ______    _____ _    _ _ _      
 | |  | |/ __ \|  ____|  / ____| |  (_) | |     
 | |__| | |  | | |__    | (___ | | ___| | |     
 |  __  | |  | |  __|    \___ \| |/ / | | |     
 | |  | | |__| | |____   ____) |   <| | | |____ 
 |_|  |_|\___\_\______| |_____/|_|\_\_|_|______|
                                                
    High Quality Engineering Skill for Autonomous AI Agents
```

[![CI](https://img.shields.io/badge/CI-Passing-brightgreen.svg?style=for-the-badge&logo=githubactions)](.github/workflows/ci.yml)
[![Protocol](https://img.shields.io/badge/Protocol-HQE%20v5.0.0-blue.svg?style=for-the-badge)](protocol/hqe-engineer.yaml)
[![License](https://img.shields.io/badge/License-Apache%202.0-yellow.svg?style=for-the-badge)](LICENSE)
[![Security](https://img.shields.io/badge/Security-Threat%20Model%20Enforced-red.svg?style=for-the-badge)](docs/SECURITY_MODEL.md)
[![Privacy](https://img.shields.io/badge/Privacy-Local%20First-purple.svg?style=for-the-badge)](PRIVACY.md)
[![Python](https://img.shields.io/badge/Python-3.10%2B-informational.svg?style=for-the-badge&logo=python)](scripts/)

<p align="center">
  <b>Evidence-first repository health auditing, security vulnerability discovery, architectural synthesis, and verified minimal-change remediation for autonomous AI agents.</b>
</p>

[Quickstart](#-quickstart--installation) • [Operating Modes](#-operating-modes) • [Architecture](#-architecture--repository-structure) • [Protocol Validation](#-protocol-validation) • [Security Model](#-security--trust-model) • [Documentation](#-canonical-documentation) • [Legal](#-legal--compliance)

---

</div>

## 📑 Table of Contents
- [Executive Overview](#-executive-overview)
- [Key Capabilities](#-key-capabilities)
- [Non-Negotiable Operating Principles](#-non-negotiable-operating-principles)
- [Operating Modes & Routing](#-operating-modes--routing)
- [Protocol Validation](#-protocol-validation)
- [Architecture & Repository Structure](#-architecture--repository-structure)
- [Quickstart & Installation](#-quickstart--installation)
- [Finding & Artifact Model](#-finding--artifact-model)
- [CLI Helper Tools](#-cli-helper-tools)
- [Security & Trust Model](#-security--trust-model)
- [CI/CD & Verification](#-cicd--verification)
- [Canonical Documentation](#-canonical-documentation)
- [Legal & Compliance](#-legal--compliance)

---

## 🎯 Executive Overview

**HQE (`/HQE`)** is a portable, production-grade agent skill that equips AI coding agents with the rigor, skepticism, and methodical precision of a Principal Staff Software Engineer and Principal Security Auditor.

Built directly from and validated against **HQE Engineer Protocol v5.0.0** ([`protocol/hqe-engineer.yaml`](protocol/hqe-engineer.yaml)), this skill eliminates shallow, hallucinated code reviews by enforcing **mandatory static/dynamic evidence**, **explicit uncertainty tagging** (`[FACT]`, `[INFERENCE]`, `[HYPOTHESIS]`, `[NEEDS_VERIFICATION]`), **1–10 health scoring**, **severity gates with likelihood models**, **security taint chains**, **change budgets ($\le 5$ files)**, and **anti-regression controls**.

---

## ⚡ Key Capabilities

- 🔍 **Evidence-First Discovery**: Zero unsubstantiated claims. Every finding requires an exact file path, verified line range or anchor, and 2–5 line code snippet.
- 🛡️ **Defensive Security Review**: Deep audit of trust boundaries, authentication flows, injection surfaces, secret leaks, and complete source-to-sink taint chains.
- 🚦 **Severity Gates & Likelihood Models**: CRITICAL/HIGH findings require explicit preconditions, exploitability, blast radius, and likelihood justification.
- 🧱 **Architectural Cohesion**: Identification of circular dependencies, boundary leaks, tight coupling, and abstraction violations.
- 🛠️ **Minimal-Change Remediation**: Surgical root-cause fixes adhering to a strict change budget ($\le 5$ files) and anti-regression rules (`[BEHAVIOR CHANGE]`, `[NEW_DEPENDENCY]`).
- 📋 **Canonical Artifact System**: Generates the 9 canonical HQE audit deliverables (Risk Register, Master TODO, Pattern Findings, Quick Wins vs Structural, Security Posture, Reliability, Testing Gaps, Unknowns, Confidence Declaration).
- 🔒 **Prompt Injection Immunity**: Treats all audited code, fixtures, comments, and instructions as passive untrusted data.
- ⚙️ **Local-First Helper Tooling**: Portable, dependency-light Python utilities with deterministic secret redaction.

---

## 📜 Non-Negotiable Operating Principles

When an AI agent activates `/HQE`, it must adhere to the core tenets specified in [`SKILL.md`](SKILL.md):

```text
1.  Inspect before asserting         8.  Minimal-change remediation bias (<=5 files)
2.  Zero hallucination guarantee     9.  Preserve repository conventions
3.  Explicit uncertainty tagging     10. Test-driven fixes & verification prerequisite
4.  Mandatory code evidence triad    11. Untrusted repository content isolation
5.  Strict secret redaction          12. Distinguish source from build/vendor artifacts
6.  Protect unrelated worktree state 13. Graceful degradation & blocker instrumentation
7.  Execution honesty                14. Reproducibility run manifest generation
```

---

## 🕹️ Operating Modes & Routing

Invoke `/HQE` with any of the following modes:

| Mode | Command | Objective & Focus Area | Workflow Reference |
| :--- | :--- | :--- | :--- |
| **Audit** | `/HQE audit` | Comprehensive repository audit emitting canonical artifacts. | [`workflows/full-audit.md`](workflows/full-audit.md) |
| **Security** | `/HQE security` | Attack surface, trust boundaries, auth logic, taint chains. | [`workflows/security-audit.md`](workflows/security-audit.md) |
| **PR Review** | `/HQE pr-review` | Phase -1 diff harvest, changed files, and affected adjacent code. | [`workflows/pr-review.md`](workflows/pr-review.md) |
| **Targeted** | `/HQE targeted` | Deep dive into a specific subsystem, bug symptom, or suspect file. | [`workflows/targeted-bug-hunt.md`](workflows/targeted-bug-hunt.md) |
| **Remediate**| `/HQE remediate`| Implement verified, minimal root-cause fixes respecting change budget. | [`workflows/remediation-run.md`](workflows/remediation-run.md) |
| **Verify** | `/HQE verify` | Rigorous Tier 1/2/3 verification proving/disproving fixes. | [`workflows/verification-run.md`](workflows/verification-run.md) |
| **Incident** | `/HQE incident` | Stop-the-line triage, containment, and incident mini-report. | [`workflows/incident-response.md`](workflows/incident-response.md) |
| **Debug** | `/HQE debug` | Systematic exception and stack trace diagnosis. | [`workflows/debug-error.md`](workflows/debug-error.md) |
| **Trace** | `/HQE trace` | Multi-hop execution trace and regression isolation. | [`workflows/trace-regression.md`](workflows/trace-regression.md) |
| **Handoff** | `/HQE handoff` | Produce an unambiguous, implementation-ready agent handoff ledger. | [`workflows/handoff-generation.md`](workflows/handoff-generation.md) |
| **Perf** | `/HQE performance` | Hot paths, algorithmic complexity, I/O bottlenecks, memory bloat. | [`workflows/performance-audit.md`](workflows/performance-audit.md) |
| **Reliability**| `/HQE reliability` | Timeouts, retries, race conditions, idempotency, data consistency. | [`references/reliability-review.md`](references/reliability-review.md) |

---

## 🔍 Protocol Validation

Validate the embedded canonical HQE protocol and active Draft-7 JSON schema:

```bash
# Validate protocol YAML against schema
python3 protocol/validate.py protocol/hqe-engineer.yaml

# Validate schema structure
python3 protocol/validate.py --schema

# Run strict protocol bundle integrity checks
python3 scripts/validate_protocol_bundle.py --strict-schema-metadata

# Run protocol contract tests
pytest tests/test_protocol_contract.py tests/test_protocol_skill_parity.py
```

---

## 🏛️ Architecture & Repository Structure

```text
Skill-HQE/
├── 📄 SKILL.md                  # Root skill operational projection & control plane
├── 📄 LICENSE                   # Apache-2.0 open-source license
├── 📄 NOTICE                    # Attribution, source lineage, and copyright notice
├── 📄 VERSION                   # Semantic version (4.2.1)
├── 📄 CHANGELOG.md              # Historical version changelog
├── 📄 pyproject.toml            # Project packaging & test configuration
├── 📄 requirements-dev.txt      # Development & validation dependencies
│
├── 📂 protocol/                 # Embedded canonical HQE Protocol v4.2.1
│   ├── hqe-engineer.yaml        # Active canonical protocol YAML
│   ├── hqe-engineer-schema.json # Active Draft-7 JSON schema
│   ├── validate.py              # Canonical protocol validator
│   ├── README.md                # Protocol documentation
│   ├── VALIDATORS.md            # Validator usage specifications
│   └── SOURCE_CHECKSUMS.sha256  # Source cryptographic checksums
│
├── 📂 docs/                     # Canonical engineering documentation
│   ├── ARCHITECTURE.md          # Architectural specification and layer design
│   ├── CAPABILITY_MAPPING.md    # Source-to-skill capability mapping audit
│   ├── MIGRATION_FROM_HQE_WORKBENCH.md # Migration guide from Workbench
│   ├── DESIGN_DECISIONS.md      # Architectural Decision Records (ADRs)
│   ├── SOURCE_AUDIT.md          # Licensing, lineage, and checksum audit
│   ├── DEVELOPER_GUIDE.md       # Developer and extension manual
│   ├── FINDING_SPECIFICATION.md # Finding format, taxonomy, and severity rubric
│   ├── SECURITY_MODEL.md        # Security boundaries and isolation architecture
│   ├── THREAT_MODEL.md          # STRIDE threat model and risk mitigations
│   └── USER_GUIDE.md            # Comprehensive user manual
│
├── 📂 references/               # Modular knowledge base loaded on-demand
│   ├── hqe-protocol.md          # Human-readable protocol projection
│   ├── audit-methodology.md     # Execution lifecycle
│   ├── evidence-standard.md     # Code snippet and evidence requirements
│   ├── severity-confidence-effort.md # Severity gate, confidence, and effort matrix
│   ├── health-scoring.md        # Evidence-backed 1–10 health scoring
│   ├── change-control.md        # Change budget & anti-regression rules
│   ├── blockers-and-unknowns.md # No-stall instrumentation guidelines
│   ├── pre-delivery-gates.md    # Pre-delivery checklist & definition of done
│   ├── output-controls.md       # Output caps and overflow consolidation
│   ├── patch-packaging.md       # Unified diff patch packaging contract
│   ├── quality-gates.md         # Engineering evaluation gates
│   ├── reasoning-methodologies.md # 5W1H, CAGEERF, FOCUS, REACT, SCAMPER
│   ├── security-review.md       # Security review checklist & taint chains
│   ├── reliability-review.md    # Fault tolerance, retries, and data consistency
│   ├── observability-review.md  # Logging, metrics, tracing, and alerts
│   ├── performance-review.md    # Hot paths, I/O, and algorithmic efficiency
│   ├── architecture-review.md   # Modularity, coupling, and boundaries
│   ├── testing-review.md        # Test gap analysis & fixture realism
│   ├── dependency-review.md     # Supply chain and dependency risks
│   ├── ci-cd-review.md          # Pipeline security, permissions, and gates
│   ├── documentation-review.md  # Documentation validation vs reality
│   ├── ux-dx-review.md          # CLI ergonomics, errors, and onboarding
│   ├── boot-startup-review.md   # Boot panics and environment initialization
│   ├── technical-debt-review.md # Cyclomatic complexity and dead code
│   ├── remediation.md           # Minimal-change fix engineering
│   ├── verification.md          # Verification tiers (Tier 1/2/3)
│   ├── large-repo-strategy.md   # Triage and coverage ledger for >50 files
│   ├── prompt-injection-defense.md # Untrusted content defense rules
│   ├── source-lineage.md        # Source provenance and lineage notes
│   └── 📂 language-guides/      # Language-specific diagnostic guides (9 languages)
│
├── 📂 workflows/                # Phased procedural reasoning playbooks
│   ├── full-audit.md            # End-to-end full audit workflow
│   ├── targeted-bug-hunt.md     # Focused diagnostic workflow
│   ├── security-audit.md        # Dedicated security audit playbook
│   ├── architecture-audit.md    # Architecture evaluation playbook
│   ├── performance-audit.md     # Performance audit playbook
│   ├── dependency-audit.md      # Dependency & supply chain audit
│   ├── ci-audit.md              # CI/CD pipeline audit
│   ├── testing-audit.md         # Test suite & coverage audit
│   ├── documentation-audit.md   # Documentation accuracy audit
│   ├── remediation-run.md       # Safe remediation execution workflow
│   ├── verification-run.md      # Verification & test proof workflow
│   ├── regression-analysis.md   # Regression isolation workflow
│   ├── pr-review.md             # Pull request diff analysis workflow
│   ├── incident-response.md     # Stop-the-line incident workflow
│   ├── debug-error.md           # Error & exception debugging playbook
│   ├── trace-regression.md      # Multi-hop execution trace playbook
│   └── handoff-generation.md    # Agent-to-agent task delegation workflow
│
├── 📂 templates/                # Markdown report and artifact templates
│   ├── finding.md               # Standard single finding template
│   ├── report.md                # Full audit executive report template
│   ├── handoff.md               # Comprehensive agent handoff template
│   ├── run-manifest.md          # Scan manifest template
│   ├── risk-register.md         # Risk register template
│   ├── master-todo-backlog.md   # Master TODO backlog template
│   ├── pattern-findings.md      # Cross-cutting pattern findings template
│   ├── quick-wins-vs-structural.md # Quick wins template
│   ├── security-posture-summary.md # Security posture template
│   ├── reliability-summary.md   # Reliability summary template
│   ├── testing-gaps.md          # Testing gaps template
│   ├── unknowns-verification.md # Blockers & unknowns template
│   ├── confidence-declaration.md # Confidence declaration template
│   ├── session-log.md           # Session continuity log template
│   ├── redaction-log.md         # Redaction log template
│   ├── patch-action.md          # Single-finding patch action template
│   ├── remediation-plan.md      # Remediation plan template
│   ├── validation-report.md     # Validation report template
│   └── incident-mini-report.md  # Incident mini-report template
│
├── 📂 schemas/                  # Draft-07 JSON schemas for machine artifacts
│   ├── finding.schema.json      # Single finding schema with severity gate
│   ├── findings.schema.json     # Findings collection schema
│   ├── run-manifest.schema.json # Run manifest schema
│   ├── handoff.schema.json      # Agent handoff schema
│   ├── session-log.schema.json  # Cross-run session log schema
│   ├── redaction-log.schema.json # Redaction log schema
│   └── report.schema.json       # Structured audit report schema
│
├── 📂 scripts/                  # Portable Python CLI helper tools
│   ├── check_skill.py           # Skill structure & link validator
│   ├── detect_manifests.py      # Multi-ecosystem manifest detector (22+ ecosystems)
│   ├── detect_test_commands.py  # Test & verification command detector
│   ├── inventory_repo.py        # Comprehensive repository indexer & classifier
│   ├── local_risk_scan.py       # Safe static risk scanner
│   ├── redact_secrets.py        # Regex-based deterministic secret redactor
│   ├── summarize_tree.py        # Subsystem tree summarizer
│   ├── validate_findings.py     # JSON findings schema validator
│   ├── validate_manifest.py     # Run manifest validator
│   ├── validate_session_log.py  # Session log validator
│   ├── validate_semantics.py    # Cross-field semantic validator
│   ├── validate_protocol_bundle.py # Protocol bundle validator
│   └── package_skill.py         # Release packager (zero cache/git debris)
│
└── 📂 tests/                    # Automated tests and acceptance fixtures
    ├── test_structure.py        # Repository structure tests
    ├── test_schemas.py          # JSON schema validation tests
    ├── test_semantics.py        # Semantic invariant tests
    ├── test_inventory.py        # Inventory classification tests
    ├── test_manifests.py        # Ecosystem manifest tests
    ├── test_local_risk_scan.py  # Static risk scan tests
    ├── test_redaction.py        # Secret redaction tests
    ├── test_links.py            # Relative markdown link integrity tests
    ├── test_packaging.py        # Clean packaging tests
    ├── test_protocol_contract.py # Canonical protocol contract tests
    ├── test_protocol_skill_parity.py # Skill-to-protocol parity tests
    ├── 📂 fixtures/             # Standard test payloads
    └── 📂 acceptance/           # Realistic polyglot acceptance scenarios
```

---

## 🚀 Quickstart & Installation

### 1. Installation into Host AI Agent

```bash
# Antigravity CLI / Gemini CLI:
cp -r /path/to/Skill-HQE ~/.gemini/antigravity-cli/builtin/skills/hqe

# Kimi Code / oh-my-kimi:
cp -r /path/to/Skill-HQE ~/.agents/skills/hqe

# Claude Code / Cursor / Windsurf:
cp -r /path/to/Skill-HQE /your/workspace/.agents/skills/hqe
```

### 2. Basic Invocation Examples

```text
# Run a full repository audit
/HQE audit

# Run a dedicated security scan
/HQE security

# Review uncommitted changes or incoming PR
/HQE pr-review

# Remediate a verified finding with minimal diff
/HQE remediate HQE-BUG-014
```

---

## 📊 Finding & Artifact Model

Findings are categorized under the **HQE Finding Taxonomy**:
`HQE-(BOOT|SEC|BUG|REL|PERF|UX|DX|DOC|DEBT|DEPS)-<INDEX>`

```json
{
  "id": "HQE-SEC-001",
  "title": "Hardcoded JWT Secret Fallback in Authentication Handler",
  "category": "SEC",
  "severity": "HIGH",
  "confidence": "FACT",
  "status": "CONFIRMED",
  "affected_component": "crates/hqe-core/src/auth.rs",
  "preconditions": ["Service deployed with unset JWT_SECRET environment variable"],
  "exploitability": "Trivial via forged signature",
  "blast_radius": "Complete authentication bypass for all user sessions",
  "likelihood": "High",
  "likelihood_justification": "Production containers default to empty env unless injected",
  "exposure_evidence": "auth.rs#L52 entrypoint exposed to public HTTP listener",
  "evidence": [
    {
      "path": "crates/hqe-core/src/auth.rs",
      "start_line": 52,
      "end_line": 56,
      "snippet": "let secret = std::env::var(\"JWT_SECRET\").unwrap_or_else(|_| \"dev-insecure-secret\".to_string());"
    }
  ],
  "observed_behavior": "Service falls back to a static dev secret when JWT_SECRET is unset.",
  "expected_behavior": "Service must fail fast with a fatal startup error if JWT_SECRET is unset in production.",
  "root_cause": "Permissive default fallback in auth initialization.",
  "impact": "Allows arbitrary authentication token forgery.",
  "remediation": "Replace fallback with explicit error propagation.",
  "validation": ["cargo test --package hqe-core test_auth_missing_secret_fails"],
  "effort": "S",
  "regression_risk": "Low"
}
```

---

## 🛠️ CLI Helper Tools

All helper scripts in `scripts/` are standalone, portable Python 3.10+ utilities:

```bash
# 1. Inventory repository files with category breakdown
./scripts/inventory_repo.py /path/to/repo

# 2. Detect project manifests across 22+ ecosystems
./scripts/detect_manifests.py /path/to/repo

# 3. Detect available verification and test commands
./scripts/detect_test_commands.py /path/to/repo

# 4. Run safe local static risk scan
./scripts/local_risk_scan.py /path/to/repo

# 5. Redact secrets from file or stdin
./scripts/redact_secrets.py /path/to/file

# 6. Validate findings JSON against schema & semantic rules
./scripts/validate_findings.py findings.json
./scripts/validate_semantics.py findings.json

# 7. Check internal structural integrity of Skill-HQE
./scripts/check_skill.py .

# 8. Package clean release bundle
./scripts/package_skill.py --output /tmp/Skill-HQE.zip
```

---

## 🔐 Security & Trust Model

The HQE Skill is hardened against adversarial codebase manipulation:

- 🛡️ **Untrusted Codebase Boundary**: Comments, fixtures, and documentation in audited repositories cannot instruct the agent to execute malicious commands or bypass safety rules. See [`docs/SECURITY_MODEL.md`](docs/SECURITY_MODEL.md) and [`references/prompt-injection-defense.md`](references/prompt-injection-defense.md).
- 🔑 **Automated Secret Redaction**: Credentials and tokens discovered during audits are automatically redacted (`REDACTED_<TYPE>_<COUNT>`).
- 📁 **Working Tree Protection**: Pre-flight checks ensure uncommitted developer work is never overwritten.
- 🎯 **STRIDE Analysis**: Comprehensive threat matrix documented in [`docs/THREAT_MODEL.md`](docs/THREAT_MODEL.md).

---

## 🧪 CI/CD & Verification

Run the full local verification test suite:

```bash
# Run all unit, contract, semantic, and acceptance tests
pytest -v

# Verify skill completeness, schema validity, and markdown links
./scripts/check_skill.py .
```

---

## 📚 Canonical Documentation

- 📐 [**Architecture Specification**](docs/ARCHITECTURE.md)
- 🗺️ [**Capability Mapping Document**](docs/CAPABILITY_MAPPING.md)
- 🔄 [**Migration from HQE-Workbench**](docs/MIGRATION_FROM_HQE_WORKBENCH.md)
- 💡 [**Design Decisions (ADRs)**](docs/DESIGN_DECISIONS.md)
- 🔍 [**Source Audit & Checksums**](docs/SOURCE_AUDIT.md)
- 📖 [**User Guide & Manual**](docs/USER_GUIDE.md)
- 🛠️ [**Developer & Extension Guide**](docs/DEVELOPER_GUIDE.md)
- 🏷️ [**Finding Specification & Taxonomy**](docs/FINDING_SPECIFICATION.md)
- 🛡️ [**Security Model**](docs/SECURITY_MODEL.md)
- 🎯 [**STRIDE Threat Model**](docs/THREAT_MODEL.md)

---

## ⚖️ Legal & Compliance

- **License**: Distributed under the [Apache License 2.0](LICENSE).
- **Notice & Lineage**: See [NOTICE](NOTICE) for copyright and attribution.
- **Terms of Service**: Governed by the [Terms of Service & Acceptable Use Policy](TERMS_OF_SERVICE.md).
- **Privacy Policy**: Read our [Local Data Handling Policy](PRIVACY.md).
- **Vulnerability Disclosure**: Read [SECURITY.md](SECURITY.md) for reporting guidelines.
- **Code of Conduct**: Governed by the [Contributor Covenant v2.1](CODE_OF_CONDUCT.md).
- **Contributions**: Follow our [Contribution Guide](CONTRIBUTING.md).

<div align="center">
  <sub>Built for the next generation of autonomous, reliable, and secure AI software engineering.</sub>
</div>
