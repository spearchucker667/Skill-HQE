# Research Quality Gate

> **Source lineage:** HQE-Workbench `mcp-server/prompts/server/resources/gates/research-quality/`. Paraphrased for HQE Skill use.

## Purpose / When to Activate

The Research Quality gate ensures that factual claims are backed by credible, cited sources. Activate it for research tasks, literature reviews, technology comparisons, and any output that relies on external facts.

## Pass Criteria

- At least three credible sources support factual claims.
- Publication dates are included for time-sensitive information.
- A distinction is made between primary and secondary sources.
- Facts are cross-referenced across multiple sources.
- Statistical claims include context.
- Authoritative sources are preferred (academic journals, official docs, government data, established outlets).

## Forbidden Patterns / Failure Modes

| Pattern | Risk |
| :--- | :--- |
| Claims without citation | Unverifiable assertions. |
| Single source for controversial facts | Confirmation bias. |
| Missing publication dates | Stale or obsolete information. |
| Unclear distinction between source types | Misrepresented authority. |
| Statistical claims without context | Misleading conclusions. |

## Activation Rules

- **Artifact types:** research summaries, technology evaluations, comparison documents.
- **Workflow triggers:** research, analysis.
- **Explicit request:** required; this gate should be requested explicitly for research-heavy tasks.

## Retry / Escalation Guidance

1. **First failure:** Add citations and dates.
2. **Second failure:** Cross-check claims against a second authoritative source.
3. **Third failure (max 3 attempts):** Mark unresolved claims as `[HYPOTHESIS]` or `[NEEDS_VERIFICATION]` and document the search scope and gaps.
