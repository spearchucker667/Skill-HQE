# Code Review Methodology

> **Source lineage:** HQE Workbench review practices and the HQE finding taxonomy. Defines a repeatable, evidence-first approach to reviewing code changes and existing source.

## Purpose

The Code Review methodology provides a structured lens for evaluating source code in an HQE audit. It maps observations to the HQE finding categories, assigns severity using explicit evidence thresholds, and ensures that critiques are anchored to concrete code locations rather than preference or intuition.

Use this methodology for PR reviews, targeted audits, pre-delivery gates, and any task where source code must be evaluated for correctness, safety, maintainability, or operational risk.

## When to Activate

- The audit scope includes source files, diffs, patches, or generated code.
- A PR review workflow is triggered.
- Remediation output must be validated before hand-off.
- A gate such as `references/gates/code-quality.md` or `references/gates/pr-security.md` is applied.

## Review Steps

| Step | Question to Answer | Required |
| :--- | :--- | :--- |
| **1. Orientation** | What language, framework, entrypoints, and conventions does the code use? | Yes |
| **2. Boundary Scan** | Where does untrusted input cross a trust boundary? | Yes for SEC; optional otherwise |
| **3. Correctness Check** | Does the code do what it claims? Are edge cases handled? | Yes |
| **4. Reliability Check** | Are errors handled, resources cleaned up, and failures observable? | Yes |
| **5. Performance Check** | Are there algorithmic, I/O, or memory issues on hot paths? | Optional |
| **6. Maintainability Check** | Is the code readable, consistent, and within the change budget? | Yes |
| **7. Security Check** | Are injection sinks protected, secrets absent, and authz enforced? | Yes |
| **8. Synthesis** | Summarize findings, severity, confidence, and remediation paths. | Yes |

## Severity Classification Guidance

Align every finding with the HQE severity scale using the evidence thresholds below. CRITICAL and HIGH findings must satisfy the additional severity gate fields defined in `schemas/finding.schema.json`.

| Severity | Evidence threshold | Typical scope |
| :--- | :--- | :--- |
| **CRITICAL** | Exploitable without authentication or user interaction; causes severe data loss, remote code execution, or systemic failure. | `SEC`: unauthenticated RCE, mass data exfiltration. `BOOT`: service cannot start in any supported environment. |
| **HIGH** | Reaches a dangerous sink or breaks core functionality under realistic preconditions; requires prompt action. | `SEC`: authenticated injection or authz bypass. `BUG`: reproducible crash or data corruption. `REL`: cascading failure path. |
| **MEDIUM** | Real defect or risk, but limited blast radius, requires specific preconditions, or is a quality barrier. | `PERF`: N+1 query on a non-trivial list. `UX`: confusing error that misdirects users. `DEBT`: abstraction leak that slows change. |
| **LOW** | Minor issue; cosmetic, narrowly scoped, or easily worked around. | `DOC`: stale comment. `DX`: inconsistent naming. `DEPS`: outdated patch-level dependency with no known exploit. |
| **INFO** | Observation, suggestion, or context for future maintainers; no immediate action required. | `INFO`: note about a design trade-off, alternative pattern, or historical decision. |

## HQE Category Mapping

Use the categories below to classify findings consistently. Every finding ID must match the pattern `HQE-<CATEGORY>-<NNN>`.

| Category | Focus | Example triggers |
| :--- | :--- | :--- |
| **BOOT** | Startup, initialization, environment, and deployment bootstrap. | Missing env var handling, failed imports, container startup errors. |
| **SEC** | Security vulnerabilities, trust boundaries, secrets, and taint chains. | Injection, authz bypass, hardcoded secrets, missing validation. |
| **BUG** | Functional defects and incorrect behavior. | Logic errors, off-by-one, null dereferences, state corruption. |
| **REL** | Reliability, availability, error handling, and observability. | Uncaught exceptions, missing retries, silent failures. |
| **PERF** | Performance, throughput, latency, and resource consumption. | N+1 queries, unbounded loops, memory leaks. |
| **UX** | User experience and interface behavior. | Confusing flows, missing feedback, accessibility barriers. |
| **DX** | Developer experience, tooling, and maintainability. | Poor naming, missing tests, brittle scripts. |
| **DOC** | Documentation accuracy and completeness. | Stale README, missing API docs, misleading comments. |
| **DEBT** | Technical debt and design erosion. | Duplication, premature abstraction, layering violations. |
| **DEPS** | Dependencies, supply chain, and third-party risk. | Vulnerable package, unlicensed dependency, version conflict. |

## Pass Criteria

- All findings cite exact file paths, line numbers, and 2–5 line snippets.
- Severity is justified by the evidence thresholds above.
- `SEC` findings include a complete taint chain.
- CRITICAL/HIGH findings include severity gate fields.
- Remediation is minimal, safe, and includes a verification command.
- No unredacted secrets or credentials appear in evidence snippets.

## Forbidden Patterns / Failure Modes

| Pattern | Risk | Category |
| :--- | :--- | :--- |
| Hardcoded secrets in code or config | Credential exposure | `SEC` |
| Missing input validation at trust boundaries | Injection and traversal | `SEC` |
| Uncaught exceptions in request handlers | Denial of service or data inconsistency | `REL` |
| N+1 queries in list endpoints | Latency and load spikes | `PERF` |
| Functions with no error returns or logging | Silent failures | `REL` |
| Imports reaching into private internals of another module | Coupling and breakage | `DEBT` |
| Stale comments contradicting implementation | Misleading maintainers | `DOC` |

## Activation Rules

- **Artifact types:** source files, diffs, patches, scripts, infrastructure templates.
- **Workflow triggers:** PR review, targeted audit, remediation validation, pre-delivery gate.
- **Explicit request:** not required when code is in scope.

## Retry / Escalation Guidance

1. **First pass:** Apply the eight review steps and record observations without severity.
2. **Second pass:** Classify each observation by category and severity, adding evidence.
3. If a finding cannot be anchored to a concrete code location, downgrade to `INFO` or `NEEDS_VERIFICATION`.
4. If multiple HIGH/CRITICAL findings appear in the same module, escalate to the relevant deep-dive workflow (`workflows/security-audit.md`, `workflows/targeted-bug-hunt.md`).

## Compatible Frameworks / Styles

- **Compatible styles:** analytical, procedural.
- **Matching gates:** `references/gates/code-quality.md`, `references/gates/pr-security.md`, `references/gates/pr-performance.md`.
- **Often paired with:** [Critical Thinking](critical-think.md), [FOCUS](focus.md), [CAGEERF](cageerf.md).

## Example Usage in an HQE Workflow

During a **PR review**, apply the Code Review methodology as follows:

- **Orientation:** Identify the language, test framework, and conventions from the repository.
- **Boundary Scan:** Trace untrusted inputs from request handlers to sinks.
- **Correctness Check:** Verify the change matches the stated intent and handles edge cases.
- **Reliability Check:** Confirm errors are returned or logged, not swallowed.
- **Performance Check:** Flag any new unbounded loop or query pattern.
- **Maintainability Check:** Ensure naming is consistent and the change stays within the change budget.
- **Security Check:** Validate secrets hygiene and authz enforcement.
- **Synthesis:** Emit findings using `templates/finding.md` and `schemas/finding.schema.json`.
