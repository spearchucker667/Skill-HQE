# PR Review Workflow

When requested (`/HQE pr-review`), the focus shifts to changed code and its immediate context.

## Execution Model
1. **Contextualize**: Identify the PR boundaries. Read the PR description.
2. **Read Diffs**: Analyze the diffs for all changed files.
3. **Verify Context**: If a diff modifies a function, read the surrounding code in the actual file.
4. **Security Review**: Check for new injection vectors, missing auth, or leaked secrets in the diff.
5. **Architectural Review**: Does the PR violate architectural boundaries?
6. **Correctness**: Do the changes fulfill the stated purpose without breaking existing behavior?
7. **Test Coverage**: Are there new tests for new behavior?
8. **Feedback**: Generate structured feedback focusing on substantive issues, not nitpicks. Use finding schemas if appropriate.
