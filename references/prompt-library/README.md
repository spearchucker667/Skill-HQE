# HQE Prompt Library

This directory contains reusable single-shot prompts for common HQE audit tasks. Each prompt is designed to be copy-pasted into a chat interface or invoked as a concise instruction. For full workflow procedures, see `workflows/`; for detailed methodology guidance, see `references/methodologies/`.

> **Scope:** These prompts are quick-start templates. They do not replace the canonical protocol (`protocol/hqe-engineer.yaml`), skill contract (`SKILL.md`), or structured workflows.

---

## Prompt Index

| Prompt | Best For | Primary workflow |
| :--- | :--- | :--- |
| [General Audit Kickoff](#general-audit-kickoff) | Start a comprehensive repository audit. | [`workflows/full-audit.md`](../../workflows/full-audit.md) |
| [Security-Focused Audit](#security-focused-audit) | Attack-surface review and taint-chain analysis. | [`workflows/security-audit.md`](../../workflows/security-audit.md) |
| [Bug Hunt](#bug-hunt) | Isolate and reproduce a specific defect. | [`workflows/targeted-bug-hunt.md`](../../workflows/targeted-bug-hunt.md) |
| [Architecture Review](#architecture-review) | Evaluate structural design and coupling. | [`workflows/architecture-audit.md`](../../workflows/architecture-audit.md) |
| [Final Quality Gate](#final-quality-gate) | Pre-delivery verification of findings or remediation. | [`workflows/final-quality-gate.md`](../../workflows/final-quality-gate.md) |

---

## General Audit Kickoff

**Purpose:** Launch a full repository audit with explicit scope, output profile, and evidence standards.

**Prompt template:**

```text
Run an HQE full audit on this repository.

Scope: <all production code and tests / specific subsystem>
Output profile: <Brief / Standard / Exhaustive>
Focus areas: <security, reliability, performance, architecture, tests, dependencies, documentation>

Follow workflows/full-audit.md. Start with Phase 0 orientation, then proceed through
Phase 2 deep-domain review and Phase 5 finding consolidation. Produce HQE_REPORT.md,
HQE_FINDINGS.json, HQE_RUN_MANIFEST.json, and the confidence declaration.

Every finding must cite exact file paths, line numbers, and code snippets. Use the HQE
severity scale and confidence model. Stop-the-line and invoke workflows/incident-response.md
if active secrets or critical unauthenticated vulnerabilities are found.
```

---

## Security-Focused Audit

**Purpose:** Perform a focused security review with trust-boundary mapping and taint-chain tracing.

**Prompt template:**

```text
Run an HQE security audit on this repository.

Follow workflows/security-audit.md. Map all trust boundaries, then trace untrusted input
from source to sink for injection paths (SQL, OS command, eval, HTML/DOM, SSRF, template,
logging). Review authentication, authorization, secrets hygiene, cryptography, and
prompt-injection defenses.

Every SEC finding must include a complete taint chain. CRITICAL and HIGH findings must
satisfy severity gates: preconditions, exploitability, blast_radius, likelihood,
likelihood_justification, and exposure_evidence. Redact all secrets with deterministic
placeholders. Emit HQE_SECURITY_POSTURE.md, HQE_FINDINGS.json, and HQE_RUN_MANIFEST.json.
```

---

## Bug Hunt

**Purpose:** Narrowly investigate a reported symptom, reproduce it, and identify the root cause.

**Prompt template:**

```text
Run an HQE targeted bug hunt.

Symptom: <describe the failure, error message, or unexpected behavior>
Scope: <files, functions, or subsystem to inspect>

Follow workflows/targeted-bug-hunt.md. Define the scope, build a dependency map, establish
a baseline, generate ranked hypotheses, trace execution, and validate the root cause with
a reproduction command or regression test. Keep the change budget to <= 5 files if
remediation is requested.

Cite exact file paths, line numbers, and snippets. Mark uncertain root causes as
NEEDS_VERIFICATION rather than fabricating a cause.
```

---

## Architecture Review

**Purpose:** Assess structural design, component coupling, boundaries, and maintainability.

**Prompt template:**

```text
Run an HQE architecture audit on this repository.

Follow workflows/architecture-audit.md. Produce a subsystem map, then analyze boundaries,
coupling, layering, state management, API contracts, and technical-debt candidates. Avoid
prescribing speculative rewrites; prefer targeted, evidence-backed refactors.

Flag any recommended interface change with [BEHAVIOR CHANGE] and provide justification.
Emit HQE_REPORT.md, HQE_PATTERN_FINDINGS.md, HQE_RELIABILITY.md, and HQE_FINDINGS.json.
```

---

## Final Quality Gate

**Purpose:** Verify that audit findings or remediation outputs are ready for delivery.

**Prompt template:**

```text
Run the HQE final quality gate.

Follow workflows/final-quality-gate.md and apply references/quality-gates.md plus
references/pre-delivery-gates.md. Verify:

1. Every finding has valid line bounds and non-empty code snippets.
2. CRITICAL/HIGH findings satisfy severity gates.
3. SEC findings have complete taint chains.
4. Remediation changes <= 5 files and flag any [BEHAVIOR CHANGE] or [NEW_DEPENDENCY].
5. Artifacts pass schema validation:
   python3 scripts/validate_findings.py HQE_FINDINGS.json
   python3 scripts/validate_manifest.py HQE_RUN_MANIFEST.json
   python3 scripts/validate_session_log.py HQE_SESSION_LOG.json

Report pass/fail for each gate and list any blockers.
```
