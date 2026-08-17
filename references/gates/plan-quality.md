# Plan Quality Gate

> **Source lineage:** HQE-Workbench `mcp-server/prompts/server/resources/gates/plan-quality/`. Paraphrased for HQE Skill use.

## Purpose / When to Activate

The Plan Quality gate ensures that implementation plans are complete, actionable, and risk-aware. Activate it whenever producing a remediation plan, feature implementation plan, or engineering task breakdown.

## Pass Criteria

- The plan identifies files to modify.
- Implementation steps are explicit and ordered.
- Risks or assumptions are documented.
- Gaps and edge cases are addressed.
- The plan is grounded in repository evidence (file paths, line ranges).

## Forbidden Patterns / Failure Modes

| Pattern | Risk |
| :--- | :--- |
| Vague steps such as "fix the bug" | Plan cannot be executed. |
| Missing file list | Scope is undefined. |
| No risk assessment | High-risk changes proceed blindly. |
| Ignored edge cases | Regressions and omissions. |
| Plan not tied to evidence | Implementation targets may not exist. |

## Activation Rules

- **Artifact types:** implementation plans, remediation plans, task breakdowns.
- **Workflow triggers:** planning, development, remediation, architecture design.
- **Explicit request:** not required.

## Retry / Escalation Guidance

1. **First failure:** Add file-level targets, concrete steps, and a risk paragraph.
2. If the plan exceeds the HQE change budget of five files per patch unit, split it into multiple linked TODOs.
3. If risks are unknown, mark them `[NEEDS_VERIFICATION]` and define a verification step before execution.
