# Remediation

When asked to remediate or fix issues (`/HQE remediate`), you must follow a disciplined, minimal-change workflow.

## Remediation Workflow
1. **Re-verify**: Verify the finding still exists and is not already fixed.
2. **Contextualize**: Read the surrounding implementation and relevant tests. Understand the public/API compatibility constraints.
3. **Plan the Fix**: Develop the smallest coherent fix that addresses the root cause. Avoid speculative mass refactors during bug fixing.
4. **Protect Unrelated Code**: Check `git status` before editing. Ensure you do not overwrite unrelated working-tree changes.
5. **Implement**: Apply the minimal safe fix.
6. **Test**: Add or update tests to provide regression coverage.
7. **Verify**: Run targeted validation, then broader validation (e.g., test suite, build).
8. **Inspect**: Inspect the final diff.
9. **Update**: Update the finding status (e.g., to `VERIFIED` once validation passes).
10. **Report**: Report unresolved issues or failed validations. Do not hide test failures. If a failure is pre-existing, provide evidence.
