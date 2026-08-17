# Testing Audit Workflow

The `tests` audit workflow (`/HQE tests`) reviews test coverage, evaluates test quality, identifies flaky or unrealistic tests, and surfaces testing gaps that affect confidence in the codebase.

## Objective

Assess whether the test suite accurately proves the repository's correctness, reliability, and security. Focus on evidence over coverage percentages. Find tests that are missing, misleading, non-deterministic, or insecure.

## Trigger Conditions

- User invokes `/HQE tests`.
- Tests are flaky, slow, or frequently disabled.
- A release gate requires confidence in regression prevention.
- A bug escaped to production because no test covered the failure path.
- A major refactor changes how components are tested.

## Execution Model

1. **Phase 0: Test Inventory**
   - Enumerate unit, integration, end-to-end, property-based, and contract tests.
   - Identify test fixtures, mocks, fakes, and shared setup utilities.
   - **Exit criteria**: Test map organized by subsystem and test type.

2. **Phase 1: Baseline Execution**
   - Run the test suite and record pass/fail, duration, flaky behavior, and skipped tests.
   - Capture pre-existing failures to avoid misattribution.
   - **Exit criteria**: Baseline health report with reproducible command and output.

3. **Phase 2: Coverage & Gap Analysis**
   - Map untested critical paths (auth, input validation, error handling, concurrency, persistence).
   - Report qualitative coverage bands (`HIGH`, `MEDIUM`, `LOW`, `UNKNOWN`) instead of invented percentages.
   - **Exit criteria**: Prioritized list of testing gaps with file/line anchors.

4. **Phase 3: Test Quality Review**
   - Inspect assertions for tautologies, weak mocks, hidden dependencies, and unrealistic fixtures.
   - Identify tests that assert implementation details instead of behavior contracts.
   - **Exit criteria**: Quality findings with concrete test file references.

5. **Phase 4: Negative & Edge Testing**
   - Verify coverage of invalid inputs, boundary values, empty collections, malformed data, and permission failures.
   - **Exit criteria**: Missing negative-test findings.

6. **Phase 5: Security & Reliability Tests**
   - Check for tests covering injection vectors, race conditions, retries, timeouts, and failure modes.
   - **Exit criteria**: Security and reliability test-gap findings.

7. **Phase 6: Validation & Artifact Generation**
   - Confirm top gaps with code anchors and, when possible, demonstrate them with failing tests.
   - Emit testing audit artifacts.
   - **Exit criteria**: Deliverables written and pre-delivery gates satisfied.

## Required Controls / Checks

- Never fabricate coverage percentages. Use qualitative bands and exact file/line counts.
- Every bug fix must include a regression test that fails before the fix and passes after.
- Tests must be deterministic; flag tests relying on sleeps, uncontrolled network calls, race conditions, or random data without seeding.
- Fixtures and mocks must be realistic; flag tests that pass only because they mock away the actual defect.
- Secret values must never appear in test fixtures or logs; use synthetic data.
- Cite exact test file paths, test names, and the production code they are meant to protect.
- Run the actual test commands; do not claim a test passes or fails unless it was executed.

## Artifact Outputs

Use the **Standard** profile for focused test reviews and the **Exhaustive** profile for release-readiness audits.

- `HQE_REPORT.md` (testing section and executive summary)
- `HQE_TESTING_GAPS.md`
- `HQE_FINDINGS.json`
- `HQE_PATTERN_FINDINGS.md`
- `HQE_MASTER_TODO.md`
- `HQE_UNKNOWNS.md`
- `HQE_CONFIDENCE.md`
- `HQE_RUN_MANIFEST.json`
- `HQE_SESSION_LOG.json`
- `HQE_HANDOFF.md` (when remediation is requested)

## Stop-the-Line Conditions

Invoke `workflows/incident-response.md` if the testing audit reveals:

- Test fixtures or logs containing active credentials or secrets.
- A test that deletes, exfiltrates, or corrupts production data when run.
- A critical path that is entirely untested and scheduled for immediate release with known severe impact.

## Confidence Model Reminders

Tag every major claim:

- `[FACT]` — Verified by running tests or inspecting test files.
- `[INFERENCE]` — Strongly supported by gap analysis and path inspection.
- `[HYPOTHESIS]` — Suspected flakiness or gap that needs a targeted reproduction.
- `[NEEDS_VERIFICATION]` — Cannot verify without a specific environment, tool, or longer runtime.

Do not report a test as reliable or a gap as closed without direct evidence from the test suite.
