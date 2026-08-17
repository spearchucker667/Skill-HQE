# Verification

Verification is critical. Do not claim a test passed or a command succeeded unless it was actually run. Do not claim a bug is fixed until relevant verification succeeds.

## Verification Steps
1. **Targeted Tests**: Run the specific tests related to the modified behavior.
2. **Module Tests**: Run the tests for the affected package or module.
3. **Broader Suite**: Run the broader test suite if safe and practical.
4. **Static Checks**: Run lint, typecheck, and static analysis tools.
5. **Build**: Ensure the project compiles or builds successfully.
6. **Runtime Smoke Test**: If feasible and safe, run a smoke test.

## Execution Honesty
- Do not declare success from compilation alone when behavior is involved.
- Do not silently downgrade failed validation. If verification fails, the issue is not fixed.
- If you cannot verify something locally, tag it as `[NEEDS_VERIFICATION]` and provide the command/steps the user should run.
