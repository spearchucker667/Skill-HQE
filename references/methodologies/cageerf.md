# CAGEERF Methodology

> **Source lineage:** HQE-Workbench `mcp-server/prompts/server/resources/methodologies/cageerf/`. Paraphrased for HQE Skill use.

## Purpose

CAGEERF is a general-purpose, phase-based methodology for structured problem solving. It ensures that an investigation or plan moves from situational awareness through analysis, goals, execution, evaluation, and refinement without skipping essential context.

Use CAGEERF for complex audits, remediation design, architecture reviews, and any task where the final output must be actionable and measurable.

## Phases / Steps

| Phase | Question to Answer | Required |
| :--- | :--- | :--- |
| **C — Context** | What is the situation, environment, background, and set of constraints? | Yes |
| **A — Analysis** | What is the systematic examination of the problem or opportunity? | Yes |
| **G — Goals** | What specific, measurable objectives define success? | Yes |
| **E — Execution** | What practical approach and concrete steps will be taken? | Yes |
| **E — Evaluation** | How will success be measured and validated? | Optional |
| **R — Refinement** | How will the approach be iterated and improved? | Optional |

Execution dependencies typically flow: Context → Analysis → Goals → Execution → Evaluation → Refinement.

## Judge-Prompt Guidance

When reviewing a CAGEERF-shaped artifact, verify:

1. **Context completeness** — environmental factors, stakeholders, and constraints are identified.
2. **Analysis depth** — multiple perspectives are considered, root causes are traced, and evidence is evaluated.
3. **Goal specificity** — objectives are quantifiable, success criteria are defined, and timelines are stated.
4. **Execution feasibility** — resources, risks, and detailed implementation steps are included.
5. **Phase coverage** — all required phases are present and logically ordered.

## Compatible Frameworks / Styles

- **Compatible styles:** analytical, procedural, reasoning.
- **Matching gate:** `references/gates/framework-compliance.md`.
- **Often paired with:** [Plan Quality](../gates/plan-quality.md), [Technical Accuracy](../gates/technical-accuracy.md).

## Example Usage in an HQE Workflow

During a **security audit**, apply CAGEERF as follows:

- **Context:** Target application type, runtime, trust boundaries, and data sensitivity.
- **Analysis:** Taint-chain analysis from untrusted sources to sinks.
- **Goals:** Identify all HIGH/CRITICAL findings with exposure evidence and taint chains.
- **Execution:** Run static scans, manual code review, and targeted tests.
- **Evaluation:** Validate findings with reproduction commands or regression tests.
- **Refinement:** Re-scan after remediation to confirm closure.

Output the final report using `templates/report.md` and the finding list using `schemas/findings.schema.json`.
