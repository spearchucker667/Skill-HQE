# Code Quality Gate

> **Source lineage:** HQE-Workbench `mcp-server/prompts/server/resources/gates/code-quality/`. Paraphrased for HQE Skill use.

## Purpose / When to Activate

The Code Quality gate ensures that generated or modified code is readable, maintainable, and follows basic best practices. Activate it for any code-generation, debugging, or refactoring task.

## Pass Criteria

- Error handling and input validation are present.
- Complex logic has inline comments explaining intent.
- Naming conventions are consistent with the surrounding codebase.
- Edge cases and boundary conditions are considered.
- Readability is prioritized over cleverness.
- Functions and modules include basic documentation or docstrings.
- Security best practices are followed (input sanitization, no hardcoded secrets).

## Forbidden Patterns / Failure Modes

| Pattern | Risk |
| :--- | :--- |
| Missing error handling | Silent failures and unhandled exceptions. |
| No input validation | Invalid data propagates through the system. |
| Inconsistent naming | Cognitive overhead and integration errors. |
| Clever one-liners without comments | Future maintainers cannot reason about the code. |
| Ignored edge cases | Latent bugs on boundary inputs. |

## Activation Rules

- **Artifact types:** source files, code snippets, scripts, patches.
- **Workflow triggers:** code generation, debugging, refactoring, remediation.
- **Explicit request:** not required.

## Retry / Escalation Guidance

1. **First failure:** Add comments, validation, and error handling; rename symbols for consistency.
2. **Second failure (max 2 attempts):** Reduce scope to a single function or file and rerun the gate before expanding.
3. If structural issues persist, route to `references/quality-gates.md` and apply the deeper code-quality checklist.
