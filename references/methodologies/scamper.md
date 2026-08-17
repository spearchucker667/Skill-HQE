# SCAMPER Methodology

> **Source lineage:** HQE-Workbench `mcp-server/prompts/server/resources/methodologies/scamper/`. Paraphrased for HQE Skill use.

## Purpose

SCAMPER is a creative problem-solving framework that generates alternatives by applying seven transformation techniques to an existing solution or situation. It is useful when the goal is innovation, option generation, or breaking out of local optima.

Use SCAMPER for remediation design alternatives, feature brainstorming, architecture refactoring options, and any task that benefits from structured creativity.

## Phases / Steps

| Technique | Question to Answer | Priority |
| :--- | :--- | :--- |
| **S — Substitute** | What can be replaced or swapped with an alternative? | Medium |
| **C — Combine** | What can be merged or integrated? | Medium |
| **A — Adapt** | What can be borrowed or learned from another context? | High |
| **M — Modify** | What can be enhanced, emphasized, or altered? | Medium |
| **P — Put to other uses** | How else could this be applied? | Low |
| **E — Eliminate** | What can be removed or simplified? | Medium |
| **R — Reverse** | What can be rearranged or approached from the opposite direction? | Low |

Execution dependencies typically flow through all seven techniques in order, producing a creative synthesis at the end.

## Judge-Prompt Guidance

When reviewing a SCAMPER-shaped artifact, verify:

1. **Substitution creativity** — alternatives are innovative yet viable.
2. **Combination synergy** — merged ideas create more value than the individual parts.
3. **Adaptation relevance** — borrowed ideas are contextually appropriate.
4. **Modification enhancement** — proposed changes are measurable and justified.
5. **Alternative-use viability** — new applications are practical.
6. **Elimination benefit** — removals simplify without losing essential functionality.
7. **Reversal innovation** — reversed arrangements provide new perspectives.

## Compatible Frameworks / Styles

- **Compatible styles:** creative, analytical.
- **Matching gate:** `references/gates/framework-compliance.md`.
- **Often paired with:** [Content Structure](../gates/content-structure.md), [Plan Quality](../gates/plan-quality.md).

## Example Usage in an HQE Workflow

When evaluating **alternative fixes for a fragile code path**, apply SCAMPER as follows:

- **Substitute:** Replace the custom parser with a maintained library.
- **Combine:** Merge validation layers so input is checked once at the boundary.
- **Adapt:** Adopt a state-machine pattern from a well-known reference implementation.
- **Modify:** Add explicit error states without changing the public API.
- **Put to other uses:** Reuse existing property-based tests to validate the new parser.
- **Eliminate:** Remove the deprecated fallback branch that no longer has callers.
- **Reverse:** Process events in reverse order to detect ordering bugs.

Document the evaluated options in `templates/pattern-findings.md` or the remediation plan.
