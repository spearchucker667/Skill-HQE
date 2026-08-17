# Debug Error & Exception Diagnosis Workflow

The `debug` workflow (`/HQE debug`) defines the systematic, evidence-first protocol for diagnosing runtime exceptions, panics, build failures, or test crashes. It is derived from `protocol/hqe-engineer.yaml` constraint C2 (Mandatory Evidence) and the CAGEERF/FOCUS reasoning frameworks.

## 1. Objective

Trace an observed error from its surface symptom to its root cause, produce a reproducible proof case, and either remediate the defect or emit a documented finding with a verification path.

## 2. Prerequisites

Before starting error diagnosis, confirm the following:

- [ ] The verbatim error message, exit code, and full stack trace are available.
- [ ] Operating system, runtime version, environment variables, and active flags are recorded.
- [ ] The repository builds (or the failure occurs during build).
- [ ] `protocol/hqe-engineer.yaml` and `references/reasoning-methodologies.md` are available for reference.
- [ ] Schema validators in `scripts/` are runnable (`python3 scripts/validate_findings.py`, etc.).

## 3. Entry Criteria

Begin this workflow when any of the following are true:

- User invokes `/HQE debug <error or symptom>`.
- A runtime exception, panic, segmentation fault, or test crash is reported.
- A build, lint, typecheck, or CI failure points to a specific first-party location.
- A flaky test or intermittent error needs deterministic reproduction.

## 4. Stop-the-Line Conditions

Immediately halt the debug workflow and invoke [`workflows/incident-response.md`](incident-response.md) if any of the following are found:

- Active credentials, API keys, tokens, or private keys exposed in logs, stack traces, or test output.
- A backdoor, malicious payload, or remote-code-execution path triggered by the error.
- A critical data-loss or data-corruption path reachable from the failure site.
- Evidence of active exploitation or unauthorized workflow modifications.

Flag the triggering item as `STOP-THE-LINE: [issue]` in the session log and do not proceed with normal artifact generation until incident response is complete.

## 5. Execution Model

### Phase 0: Error Ingestion

**Goal**: Capture the failure context exactly as observed.

1. **Collect crash context**:
   - Capture verbatim error message, exit code, and full stack trace.
   - Record operating system, runtime version, environment variables, and active flags.
2. **Identify top stack frames**:
   - Locate first-party codebase frames in the stack trace; filter out third-party/runtime frames unless they indicate a known bug.
   - Map filenames and line numbers to exact repository source files.
3. **Classify the error**: syntax/runtime/logic/test/build/configuration.

**Evidence to collect**:
- Verbatim error message and stack trace.
- Mapped first-party frames with `file:line`.
- Environment and runtime metadata.

**Exit criteria**:
- [ ] Error context is captured verbatim.
- [ ] First-party frames are mapped to exact repository source files.

### Phase 1: Frame & State Reconstruction

**Goal**: Reconstruct the state of the program at the failure site.

1. **Source inspection**:
   - Open source files at the exact line of failure.
   - Inspect 20 lines before and after the failure site.
   - Identify variable states, input parameters, and nullability/bounds/typing assumptions at the site of the crash.
2. **5W1H & genesis tracing**:
   - Trace backwards from the crash site to find where invalid state or unhandled data originated.
   - Inspect all intermediate function calls and transformations.
3. **Check concurrency** if the failure is timing-dependent.

**Evidence to collect**:
- Verbatim 2–5 line snippets at the failure site and origin points.
- Variable/input assumptions and their violations.
- Backward trace from crash to genesis.

**Exit criteria**:
- [ ] Failure site and nearby assumptions are documented with snippets.
- [ ] Genesis point of invalid state is identified or marked `[NEEDS_VERIFICATION]`.

### Phase 2: Hypothesis Formulation & Discriminating Proof

**Goal**: Generate and test explicit, falsifiable hypotheses.

1. **Formulate hypotheses**:
   - Generate explicit, testable hypotheses explaining the failure.
   - Apply the FOCUS framework if multiple causes are plausible.
2. **Construct Tier 2 reproduction test**:
   - Write a minimal, deterministic unit test or script that feeds the triggering input to the faulty function.
   - Run the reproduction test to confirm that it fails with the exact observed error.
3. **If execution is unavailable**, construct a Tier 3 static proof checklist.

**Evidence to collect**:
- Competing hypotheses with supporting/contradicting evidence.
- Reproduction test or static proof.
- Test result showing the failure is reproduced.

**Exit criteria**:
- [ ] Leading hypothesis is selected with a discriminating test or static proof.
- [ ] The failure is reproduced or its absence is explained.

### Phase 3: Minimal Root-Cause Remediation

**Goal**: Fix the root cause with the smallest safe change.

1. **Apply change budget**:
   - Formulate the minimal fix addressing the root cause (target: `<= 2` files).
   - Ensure edge cases (null values, empty collections, network disconnects, malformed input) are handled.
2. **Validate fix**:
   - Run the reproduction test; verify it passes.
   - Run the relevant module tests and, if safe, the broader test suite.
3. **Document finding**:
   - Record finding as `HQE-BUG-xxx` in `HQE_FINDINGS.json`.

**Evidence to collect**:
- Diff of the minimal fix.
- Verification command outputs.
- Updated finding with evidence and validation.

**Exit criteria**:
- [ ] Root cause is fixed with a minimal change.
- [ ] Reproduction test passes and no regressions are introduced.
- [ ] Finding is documented in `HQE_FINDINGS.json`.

### Phase 4: Consolidation & Artifact Generation

**Goal**: Produce clean, consistent deliverables.

1. **Deduplicate findings** by root cause.
2. **Emit debug workflow artifacts**.
3. **Validate** all JSON artifacts against schemas in `schemas/`.
4. **Update the session log** with completed, in-progress, discovered, and reprioritized items.

**Evidence to collect**:
- Final artifact set.
- Schema-validation output.
- Confidence declaration and unknowns list.

**Exit criteria**:
- [ ] All deliverables written and pre-delivery gates satisfied.
- [ ] Schema validation passes.

## 6. Required Controls / Checks

- Every diagnosis must start from the actual observed error, not a hypothetical one.
- First-party stack frames must be mapped to exact `file:line`.
- Claims must cite exact file paths, line numbers, and 2–5 line snippets.
- Reproduction tests must fail before the fix and pass after it.
- Keep the change budget to `<= 2` files unless the root cause genuinely spans more.
- Do not fix symptoms only; address the genesis of invalid state.
- Mark uncertain root causes as `[NEEDS_VERIFICATION]`.
- Run tests honestly; never report a test as passing unless it was executed.

## 7. Artifact Outputs

- `HQE_REPORT.md` (error summary, root cause, and fix)
- `HQE_FINDINGS.json`
- `HQE_RUN_MANIFEST.json`
- `HQE_SESSION_LOG.json`
- `HQE_PATTERN_FINDINGS.md` (if the diagnosis reveals recurring anti-patterns)
- `HQE_HANDOFF.md` (when handing off remediation to another agent)

Validate machine-readable artifacts with:

```bash
python3 scripts/validate_findings.py HQE_FINDINGS.json
python3 scripts/validate_manifest.py HQE_RUN_MANIFEST.json
python3 scripts/validate_session_log.py HQE_SESSION_LOG.json
```

## 8. Exit Criteria

Error diagnosis is complete when:

- [ ] All phases above have been executed or explicitly skipped with justification.
- [ ] The root cause is confirmed or explicitly marked `[NEEDS_VERIFICATION]`.
- [ ] Every claim cites exact file paths, line numbers, and 2–5 line snippets.
- [ ] A reproduction test or static proof exists.
- [ ] The fix is verified and no regressions are introduced.
- [ ] Artifacts are emitted and schema-validated.
- [ ] Stop-the-line conditions have been checked; if triggered, incident response has been invoked.
- [ ] The session log is updated with completed, in-progress, discovered, and reprioritized items.

## 9. Confidence Model Reminders

Tag every major claim:

- `[FACT]` — Directly observed error, stack frame, command output, or test result.
- `[INFERENCE]` — Reasonable deduction from direct evidence.
- `[HYPOTHESIS]` — A plausible explanation that requires a discriminating test.
- `[NEEDS_VERIFICATION]` — Not yet proven; must not be presented as the confirmed root cause.

Never claim an error is fixed until the reproduction test passes or the static proof is verified.
