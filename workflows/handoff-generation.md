# Handoff Generation

When requested (`/HQE handoff` or as part of a full audit), generate an implementation-ready handoff for another agent.

## Handoff Requirements
The handoff must be structured and unambiguous. Avoid vague language like "improve error handling" or "clean up code". Specify where, why, and how success is proven.

A handoff must include:
- **Mission**: A clear statement of the objective.
- **Repository/path**: Where the work should happen.
- **Current verified state**: The baseline context.
- **Do-not-assume rules**: Explicit warnings about untrusted context or fragile dependencies.
- **Finding inventory**: List of specific findings to address.
- **Priority order**: Execution order.
- **Files/components involved**: Targeted areas.
- **Root cause per finding**: Clear explanation of the defect.
- **Required changes**: Minimal safe fixes required.
- **Tests to add/update**: Expected testing approach.
- **Validation commands**: Exact commands to prove the fix.
- **Regression risks**: What else might break.
- **Completion criteria**: When the job is considered done.
- **Do-not rules**: Actions the agent must avoid.
- **Final reporting format**: How the agent should report back.

Use `templates/handoff.md` and `schemas/handoff.schema.json` to structure the output.
