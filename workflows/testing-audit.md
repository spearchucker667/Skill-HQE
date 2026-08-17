# Testing Audit Workflow

The `tests` audit workflow (`/HQE tests`) reviews test coverage, evaluates test quality, identifies flaky or unrealistic tests, and surfaces testing gaps that affect confidence in the codebase.

## 1. Objective

Assess whether the test suite accurately proves the repository's correctness, reliability, and security. Focus on evidence over coverage percentages. Find tests that are missing, misleading, non-deterministic, or insecure.

## 2. Prerequisites

Before starting the testing audit, confirm the following:

- [ ] Access to the full test suite, test configuration, and testing infrastructure.
- [ ] Access to production code files that the tests are meant to protect.
- [ ] A clean working directory or a defined scope of changed files for PR-based audits.
- [ ] `protocol/hqe-engineer.yaml` and `references/testing-review.md` are available for reference.
- [ ] Schema validators in `scripts/` are runnable (`python3 scripts/validate_findings.py`, etc.).
- [ ] A safe environment for running the full test suite.

## 3. Entry Criteria

Begin this workflow when any of the following are true:

- User invokes `/HQE tests`.
- Tests are flaky, slow, or frequently disabled.
- A release gate requires confidence in regression prevention.
- A bug escaped to production because no test covered the failure path.
- A major refactor changes how components are tested.

## 4. Stop-the-Line Conditions

Immediately halt the normal audit flow and invoke [`workflows/incident-response.md`](incident-response.md) if the testing audit reveals:

- Test fixtures or logs containing active credentials or secrets.
- A test that deletes, exfiltrates, or corrupts production data when run.
- A critical path that is entirely untested and scheduled for immediate release with known severe impact.

Flag the triggering item as `STOP-THE-LINE: [issue]` in the session log and do not proceed with normal artifact generation until incident response is complete.

## 5. Execution Model

### Phase 0: Test Inventory

**Goal**: Establish a complete map of the test landscape.

1. **Enumerate test kinds**:
   - Unit, integration, end-to-end, property-based, contract, and snapshot tests.
2. **Identify test support code**:
   - Fixtures, mocks, fakes, factories, shared setup utilities, and test helpers.
3. **Map tests to subsystems**:
   - Group tests by the production subsystem they exercise.
4. **Classify generated or vendored tests**:
   - Distinguish hand-written tests from generated or copied ones.

**Evidence to collect**:
- Test map organized by subsystem and test type.
- List of test support files and their roles.
- Coverage of generated/vendored test files.

**Exit criteria**:
- [ ] Test map organized by subsystem and test type exists.
- [ ] Every major subsystem has identifiable test coverage or a noted gap.

### Phase 1: Baseline Execution

**Goal**: Capture the current health of the test suite.

1. **Run the test suite**:
   - Execute the documented test command(s) and record pass/fail, duration, flaky behavior, and skipped tests.
2. **Capture pre-existing failures**:
   - Record failing tests before attributing failures to recent changes.
3. **Check CI behavior**:
   - Compare local results to CI logs if available; note environment-specific failures.

**Evidence to collect**:
- Baseline health report with reproducible command and output.
- List of pre-existing failures and skipped tests.
- Flaky-test observations with frequencies if known.

**Exit criteria**:
- [ ] Baseline health report with command and output exists.
- [ ] Pre-existing failures are recorded separately from new findings.

### Phase 2: Coverage & Gap Analysis

**Goal**: Identify which critical paths are unproven by tests.

1. **Map critical paths**:
   - Authentication, authorization, input validation, error handling, concurrency, persistence, and external integrations.
2. **Assess coverage qualitatively**:
   - Report qualitative bands (`HIGH`, `MEDIUM`, `LOW`, `UNKNOWN`) instead of invented percentages.
   - Support each band with file/line anchors or test names.
3. **Prioritize gaps**:
   - Rank gaps by risk area and blast radius.

**Evidence to collect**:
- Prioritized list of testing gaps with file/line anchors.
- Qualitative coverage bands with evidence references.

**Exit criteria**:
- [ ] Testing gaps are prioritized by risk area.
- [ ] Coverage claims are supported by code or test anchors.

### Phase 3: Test Quality Review

**Goal**: Find tests that are misleading or weak.

1. **Inspect assertions**:
   - Look for tautologies, weak equality checks, and assertions that cannot fail.
2. **Inspect mocks and fakes**:
   - Identify mocks that hide the actual defect or tests that pass only because the collaborator is faked away.
3. **Check test scope**:
   - Flag tests that assert implementation details instead of behavior contracts.
4. **Review test names and structure**:
   - Ensure tests describe behavior and are maintainable.

**Evidence to collect**:
- Quality findings with concrete test file references.
- Code snippets showing weak assertions, misleading mocks, or implementation-detail tests.

**Exit criteria**:
- [ ] Quality findings include concrete test file and test name references.
- [ ] Each finding explains why the test is misleading or weak.

### Phase 4: Negative & Edge Testing

**Goal**: Verify that invalid and boundary inputs are covered.

1. **Check invalid inputs**:
   - Look for tests covering malformed payloads, missing fields, wrong types, and out-of-range values.
2. **Check boundary values**:
   - Empty collections, zero, maximum length, null/nil, and whitespace.
3. **Check error paths**:
   - Verify that failure modes (exceptions, error codes, timeouts) are exercised.

**Evidence to collect**:
- Missing negative-test findings with production-code anchors.
- List of error paths that lack test coverage.

**Exit criteria**:
- [ ] Missing negative and edge-test findings are documented.
- [ ] Each gap is anchored to the production code path it should protect.

### Phase 5: Security & Reliability Tests

**Goal**: Verify that high-risk behaviors are explicitly tested.

1. **Check security tests**:
   - Look for tests covering injection vectors, authentication/authorization failures, and input sanitization.
2. **Check reliability tests**:
   - Look for tests covering retries, timeouts, circuit breakers, idempotency, and race conditions.
3. **Check failure-mode coverage**:
   - Verify that degraded dependency behavior is exercised.

**Evidence to collect**:
- Security and reliability test-gap findings.
- Production-code anchors for each missing test.

**Exit criteria**:
- [ ] Security and reliability test gaps are documented.
- [ ] Each gap maps to a concrete risk area.

### Phase 6: Determinism & Isolation

**Goal**: Find tests that are flaky, unsafe, or dependent on environment state.

1. **Find non-deterministic tests**:
   - Look for sleeps, uncontrolled network calls, race conditions, random data without seeding, and time-dependent assertions.
2. **Check test isolation**:
   - Identify shared mutable state between tests, leaked resources, and ordering dependencies.
3. **Find unsafe tests**:
   - Detect tests that touch production endpoints, real file systems outside temp dirs, or real databases without isolation.

**Evidence to collect**:
- Determinism and isolation findings with test file and test name references.
- Code snippets showing the problematic pattern.

**Exit criteria**:
- [ ] Non-deterministic and unsafe tests are documented.
- [ ] Each finding includes a recommended fix or isolation strategy.

### Phase 7: Validation & Artifact Generation

**Goal**: Produce clean, consistent, and internally consistent deliverables.

1. **Confirm top gaps** with code anchors and, when possible, demonstrate them with failing tests.
2. **Deduplicate findings** by root cause.
3. **Emit testing audit artifacts**.
4. **Validate** all JSON artifacts against schemas in `schemas/`.

**Evidence to collect**:
- Final artifact set.
- Schema-validation output.
- Confidence declaration and unknowns list.

**Exit criteria**:
- [ ] All deliverables written and pre-delivery gates satisfied.
- [ ] Schema validation passes.

## 6. Required Controls / Checks

- Never fabricate coverage percentages. Use qualitative bands and exact file/line counts.
- Every bug fix must include a regression test that fails before the fix and passes after.
- Tests must be deterministic; flag tests relying on sleeps, uncontrolled network calls, race conditions, or random data without seeding.
- Fixtures and mocks must be realistic; flag tests that pass only because they mock away the actual defect.
- Secret values must never appear in test fixtures or logs; use synthetic data.
- Cite exact test file paths, test names, and the production code they are meant to protect.
- Run the actual test commands; do not claim a test passes or fails unless it was executed.
- Use finding IDs `DX-XXX` for developer-experience issues, `MAINT-XXX` for maintainability issues, and `REL-XXX` for reliability issues.

## 7. Artifact Outputs

Use the **Standard** profile for focused test reviews and the **Exhaustive** profile for release-readiness audits.

- `HQE_REPORT.md` (testing section and executive summary)
- `HQE_TESTING_GAPS.md`
- `HQE_FINDINGS.json` (machine-readable testing findings)
- `HQE_PATTERN_FINDINGS.md`
- `HQE_MASTER_TODO.md`
- `HQE_UNKNOWNS.md`
- `HQE_CONFIDENCE.md`
- `HQE_RUN_MANIFEST.json`
- `HQE_SESSION_LOG.json`
- `HQE_HANDOFF.md` (when remediation is requested)

Validate machine-readable artifacts with:

```bash
python3 scripts/validate_findings.py HQE_FINDINGS.json
python3 scripts/validate_manifest.py HQE_RUN_MANIFEST.json
python3 scripts/validate_session_log.py HQE_SESSION_LOG.json
```

## 8. Exit Criteria

The testing audit is complete when:

- [ ] All phases above have been executed or explicitly skipped with justification.
- [ ] Every finding cites exact test files, test names, and protected production code.
- [ ] Coverage claims use qualitative bands backed by evidence.
- [ ] Artifacts are emitted and schema-validated.
- [ ] Stop-the-line conditions have been checked; if triggered, incident response has been invoked.
- [ ] The session log is updated with completed, in-progress, discovered, and reprioritized items.

## 9. Confidence Model Reminders

Tag every major claim:

- `[FACT]` — Verified by running tests or inspecting test files.
- `[INFERENCE]` — Strongly supported by gap analysis and path inspection.
- `[HYPOTHESIS]` — Suspected flakiness or gap that needs a targeted reproduction.
- `[NEEDS_VERIFICATION]` — Cannot verify without a specific environment, tool, or longer runtime.

Do not report a test as reliable or a gap as closed without direct evidence from the test suite.
