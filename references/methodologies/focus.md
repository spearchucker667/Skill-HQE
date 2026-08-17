# FOCUS Methodology

> **Source lineage:** HQE-Workbench `mcp-server/prompts/server/resources/methodologies/focus/`. Paraphrased for HQE Skill use.

## Purpose

FOCUS is a concise problem-solving framework that moves from clear problem framing through observation, conceptualization, implementation, and synthesis. It is useful when the task has a well-defined problem but multiple possible solution paths.

Use FOCUS for targeted bug hunts, feature design, and remediation planning where competing hypotheses need to be evaluated before a solution is selected.

## Phases / Steps

| Phase | Question to Answer | Required |
| :--- | :--- | :--- |
| **F — Frame** | What is the problem scope, constraints, and success criteria? | Yes |
| **O — Observe** | What relevant information, data, and patterns are available? | Yes |
| **C — Conceptualize** | What solution options exist and what are their trade-offs? | Optional |
| **U — Undertake** | Which approach is implemented step by step? | Yes |
| **S — Synthesize** | What were the results, learnings, and final outcomes? | Optional |

Execution dependencies typically flow: Frame → Observe → Undertake, with Conceptualize inserted before Undertake when alternatives exist, and Synthesize at the end.

## Judge-Prompt Guidance

When reviewing a FOCUS-shaped artifact, verify:

1. **Problem framing** — the scope is defined and success criteria are measurable.
2. **Observation quality** — relevant evidence is gathered before solutions are proposed.
3. **Solution quality** — multiple approaches are considered and trade-offs are documented.
4. **Implementation clarity** — the chosen approach is executed in ordered steps.
5. **Synthesis** — results and learnings are consolidated.

## Compatible Frameworks / Styles

- **Compatible styles:** analytical, reasoning, procedural.
- **Matching gate:** `references/gates/framework-compliance.md`.
- **Often paired with:** [Plan Quality](../gates/plan-quality.md), [Code Quality](../gates/code-quality.md).

## Example Usage in an HQE Workflow

During a **targeted bug hunt**, apply FOCUS as follows:

- **Frame:** Define the observed failure, affected component, and reproduction steps.
- **Observe:** Collect logs, stack traces, and recent commits.
- **Conceptualize:** List competing hypotheses (e.g., race condition vs. missing validation).
- **Undertake:** Write a discriminating test or probe to confirm the true cause.
- **Synthesize:** Document the confirmed root cause and the minimal fix.

Output the finding using `templates/finding.md` and the regression test as evidence in the run manifest.
