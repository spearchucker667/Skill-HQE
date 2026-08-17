# PR Performance Gate

> **Source lineage:** HQE-Workbench `mcp-server/prompts/server/resources/gates/pr-performance/`. Paraphrased for HQE Skill use.

## Purpose / When to Activate

The PR Performance gate flags performance concerns in code changes without blocking merge. It is advisory and should be activated during PR review or diff inspection when performance could degrade.

## Pass Criteria

- No O(n²) or worse nested loops without documented justification.
- Asynchronous operations are used for I/O.
- Expensive pure functions are memoized.
- No debug statements (`console.log`, `debugger`) remain in production code.
- Frontend changes consider memoization and unnecessary re-renders.
- Backend changes avoid blocking operations and unbounded queries.

## Forbidden Patterns / Failure Modes

| Pattern | Risk |
| :--- | :--- |
| Nested loops over unbounded data | Quadratic slowdown. |
| Database queries inside loops | N+1 query problem. |
| Large array operations without pagination | Memory and latency spikes. |
| Missing memoization for expensive computations | Wasted CPU on every render. |
| Object/array literals in JSX dependencies | Unnecessary re-renders. |
| Synchronous file I/O in request handlers | Event-loop blocking. |
| Unbounded queries without `LIMIT` | Denial-of-service risk. |

## Activation Rules

- **Artifact types:** PR diffs, patch files.
- **Workflow triggers:** PR review workflow.
- **Explicit request:** required; this gate is invoked explicitly for performance review.

## Retry / Escalation Guidance

1. **First failure (max 1 attempt):** Provide an advisory comment with issue type, file:line location, estimated impact, and optimization suggestion.
2. If the performance concern is severe, escalate to a blocking issue or a dedicated performance audit workflow.
3. The chain continues even when this gate flags issues because it is advisory.
