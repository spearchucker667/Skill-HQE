# HQE Workbench Quality Gates

This directory contains portable reference definitions for the quality gates defined in HQE Workbench's prompt resource library, translated into HQE Skill conventions. Each gate is a checkpoint that can be invoked between workflow steps or before a hand-off.

> **Source lineage:** HQE-Workbench `mcp-server/prompts/server/resources/gates/`. These references paraphrase the original machine-readable gate definitions; see `references/source-lineage.md` for provenance.

---

## Gate Index

| Gate | ID | Purpose | Severity |
| :--- | :--- | :--- | :--- |
| [API Documentation](api-documentation.md) | `api-documentation` | Verify API docs include endpoints, parameters, examples, errors, and auth guidance. | — |
| [Code Quality](code-quality.md) | `code-quality` | Enforce idiomatic, readable, well-commented code with basic validation. | — |
| [Content Structure](content-structure.md) | `content-structure` | Require clear headings, lists, examples, and logical flow in prose artifacts. | — |
| [Educational Clarity](educational-clarity.md) | `educational-clarity` | Ensure instructional content is pedagogical, progressive, and actionable. | — |
| [Framework Compliance](framework-compliance.md) | `framework-compliance` | Confirm responses follow an active methodology such as CAGEERF, ReACT, 5W1H, or SCAMPER. | — |
| [Plan Quality](plan-quality.md) | `plan-quality` | Validate that implementation plans identify files, steps, risks, and edge cases. | high |
| [PR Performance](pr-performance.md) | `pr-performance` | Surface algorithmic, I/O, and frontend performance concerns in diffs. | medium |
| [PR Security](pr-security.md) | `pr-security` | Block merge when security vulnerabilities or secret leakage appear in code changes. | critical |
| [Research Quality](research-quality.md) | `research-quality` | Require citations, credible sources, and cross-checked factual claims. | — |
| [Security Awareness](security-awareness.md) | `security-awareness` | Prevent common vulnerabilities and hardcoded secrets in generated code. | — |
| [Technical Accuracy](technical-accuracy.md) | `technical-accuracy` | Ensure version numbers, specifications, and technical claims are correct and cited. | — |
| [Test Coverage](test-coverage.md) | `test-coverage` | Require tests for new functions, edge cases, and both success and failure paths. | — |

---

## Using Gates in an HQE Workflow

1. **Identify the artifact type** (code, plan, documentation, PR diff, research summary).
2. **Load the matching gate** from this index.
3. **Run the pass criteria** as an explicit checklist.
4. On failure, apply the retry/escalation guidance before continuing or handing off.

For methodology-specific quality checks, combine a gate with the relevant methodology document in `references/methodologies/`.
