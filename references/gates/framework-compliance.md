# Framework Compliance Gate

> **Source lineage:** HQE-Workbench `mcp-server/prompts/server/resources/gates/framework-compliance/`. Paraphrased for HQE Skill use.

## Purpose / When to Activate

The Framework Compliance gate verifies that a response follows the active methodology or framework (CAGEERF, ReACT, 5W1H, or SCAMPER). It only activates when both a framework context and a relevant prompt category are present, preventing methodology gates from firing on trivial prompts.

## Pass Criteria

- The response explicitly addresses the required phases of the active framework.
- CAGEERF responses cover Context, Analysis, Goals, Execution, Evaluation, and Refinement.
- ReACT responses show Reason, Act, Observe, Adjust, and Continue cycles.
- 5W1H responses address Who, What, When, Where, Why, and How.
- SCAMPER responses apply Substitute, Combine, Adapt, Modify, Put to other uses, Eliminate, and Reverse.
- Systematic thinking and methodology awareness are evident.
- Iterative improvement and refinement are visible.

## Forbidden Patterns / Failure Modes

| Pattern | Risk |
| :--- | :--- |
| Framework named but not applied | Lip service; no structured thinking. |
| Missing required phases | Incomplete analysis or plan. |
| Methodology forced on trivial prompts | Unnecessary friction. |
| No explicit reasoning trace | Unverifiable progression. |

## Activation Rules

- **Artifact types:** analysis, plans, reasoning outputs, creative solutions.
- **Workflow triggers:** development, analysis, research, architecture, debugging, documentation, planning.
- **Explicit request:** not required; activates automatically when a framework context is active and the prompt category matches.
- **Framework context:** CAGEERF, ReACT, 5W1H, SCAMPER.

## Retry / Escalation Guidance

1. **First failure:** Restructure the response to explicitly label each framework phase.
2. **Second failure (max 2 attempts):** Reduce scope to the highest-priority phases and ask for a phased rewrite.
3. If the framework is ill-suited to the task, switch to a more appropriate methodology via `references/methodologies/README.md`.
