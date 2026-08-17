# Targeted Bug Hunt Workflow

The `targeted` workflow (`/HQE targeted` or `/HQE bug-hunt`) is designed for deep, narrow investigation of a specific issue, file, subsystem, or regression signal.

## Objective

Rapidly isolate, reproduce, and either remediate or report a focused defect. Avoid broad audits; limit scope to the smallest surface that can explain the symptom. Every conclusion must be anchored to repository evidence.

## Trigger Conditions

- User invokes `/HQE targeted <scope>` or `/HQE bug-hunt <scope>`.
- A specific error, stack trace, flaky test, or anomalous behavior has been reported.
- A subsystem changed recently and now exhibits unexpected behavior.
- A regression is suspected in a defined set of files.

## Execution Model

1. **Phase 0: Scope Definition**
   - Confirm the exact bounds of the hunt: files, functions, tests, inputs, and expected vs. observed behavior.
   - Record the reproduction clues, error messages, and environment details.
   - **Exit criteria**: Written scope statement and reproduction hypothesis list.

2. **Phase 1: Contextualize**
   - Read the targeted files and their direct dependencies (callers, callees, configuration, tests).
   - Build a dependency map limited to the hunt boundary.
   - **Exit criteria**: Dependency map and list of relevant symbols.

3. **Phase 2: Baseline**
   - Run the relevant tests, build commands, or lint/type checks to establish current behavior.
   - Record pre-existing failures to avoid misattribution.
   - **Exit criteria**: Baseline log with pass/fail state and command outputs.

4. **Phase 3: Hypothesize**
   - Use 5W1H or CAGEERF to decompose the defect into competing hypotheses.
   - Rank hypotheses by likelihood based on code proximity and failure signal.
   - **Exit criteria**: Ranked hypotheses with supporting and contradicting evidence.

5. **Phase 4: Trace Execution**
   - Follow data flow and control flow for the leading hypotheses.
   - Inspect state transitions, branching conditions, error handling, and concurrency.
   - **Exit criteria**: Evidence trail linking the symptom to a candidate root cause.

6. **Phase 5: Validate Hypothesis**
   - Seek static proof (exact snippet + line numbers) or write a targeted reproduction test.
   - Use FOCUS to eliminate competing hypotheses if multiple remain plausible.
   - **Exit criteria**: A confirmed or refuted root cause with evidence.

7. **Phase 6: Fix or Report**
   - If asked to remediate, follow `workflows/remediation-run.md` with a strict change budget.
   - Otherwise, emit findings using the standard schema and provide a reproduction case.
   - **Exit criteria**: Remediation patch or documented finding with verification command.

## Required Controls / Checks

- Keep the change budget to `<= 5` files unless the user explicitly approves a larger change.
- Do not perform speculative mass refactors while hunting a bug.
- Every claim must cite exact file paths, line numbers, and 2–5 line snippets.
- Add a regression test that fails before the fix and passes after it when remediation is performed.
- Run tests honestly; never report a test as passing unless it was executed.
- Mark uncertain root causes as `[NEEDS_VERIFICATION]` rather than fabricating a cause.
- Use the **Brief** profile for quick triage and the **Standard** profile when multiple findings emerge.

## Artifact Outputs

- `HQE_REPORT.md` (targeted findings and reproduction summary)
- `HQE_FINDINGS.json`
- `HQE_RUN_MANIFEST.json`
- `HQE_SESSION_LOG.json`
- `HQE_PATTERN_FINDINGS.md` (if the hunt reveals recurring anti-patterns)
- `HQE_HANDOFF.md` (when handing off remediation to another agent)

## Stop-the-Line Conditions

Pause the bug hunt and invoke `workflows/incident-response.md` if the investigation reveals:

- Active credentials or secrets embedded in the hunt scope.
- A critical security vulnerability (e.g., remote code execution, unauthenticated data access) reachable from the targeted code.
- A data-corruption or data-loss path that is actively triggered by the reported bug.

## Confidence Model Reminders

Tag every major claim:

- `[FACT]` — Directly observed code, command output, or test result.
- `[INFERENCE]` — Reasonable deduction from direct evidence.
- `[HYPOTHESIS]` — A plausible explanation that requires a discriminating test.
- `[NEEDS_VERIFICATION]` — Not yet proven; must not be presented as the confirmed root cause.

Never claim a bug is fixed until a targeted verification command passes.
