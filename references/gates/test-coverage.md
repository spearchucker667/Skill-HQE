# Test Coverage Gate

> **Source lineage:** HQE-Workbench `mcp-server/prompts/server/resources/gates/test-coverage/`. Paraphrased for HQE Skill use.

## Purpose / When to Activate

The Test Coverage gate ensures that code changes are accompanied by appropriate tests. Activate it for every code-generation, bug-fix, or refactoring task that produces or modifies functions, classes, or public APIs.

## Pass Criteria

- New functions have unit tests.
- Edge cases and error paths are covered.
- Existing coverage is maintained or improved.
- Both happy-path and failure scenarios are tested.
- Tests use clear assertions or expectations (`test`, `expect`, `assert`).

## Forbidden Patterns / Failure Modes

| Pattern | Risk |
| :--- | :--- |
| New code without any tests | Regressions go undetected. |
| Only happy-path tests | Edge-case defects survive. |
| Tests that never assert | False-positive coverage. |
| Flaky or non-deterministic tests | Unreliable CI signal. |
| Tests that mock the system under test | Tests verify mocks, not behavior. |

## Activation Rules

- **Artifact types:** source files, test files, patches.
- **Workflow triggers:** code generation, bug fixes, refactoring, remediation.
- **Explicit request:** not required.

## Retry / Escalation Guidance

1. **First failure:** Add missing tests for the new or changed behavior.
2. If coverage cannot be added due to environment constraints, document the gap in `HQE_TESTING_GAPS.md` (see `templates/testing-gaps.md`).
3. If the repository has a coverage gate in CI, run the appropriate test command (`pytest`, `cargo test`, `npm test`, etc.) and attach results as evidence.
