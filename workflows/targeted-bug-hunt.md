# Targeted Bug Hunt Workflow

The `targeted` workflow (`/HQE targeted` or `/HQE bug-hunt`) is designed for deep, narrow investigation of a specific issue, file, subsystem, or regression signal. It trades breadth for depth and is governed by the minimal-change bias in `protocol/hqe-engineer.yaml`.

## 1. Objective

Rapidly isolate, reproduce, and either remediate or report a focused defect. Avoid broad audits; limit scope to the smallest surface that can explain the symptom. Every conclusion must be anchored to repository evidence.

## 2. Prerequisites

Before starting the bug hunt, confirm the following:

- [ ] The scope is defined: files, functions, tests, inputs, and expected vs. observed behavior.
- [ ] Reproduction clues, error messages, stack traces, or flaky-test logs are available.
- [ ] The repository builds and the relevant test command is known.
- [ ] `protocol/hqe-engineer.yaml` and `references/reasoning-methodologies.md` are available for reference.
- [ ] Schema validators in `scripts/` are runnable (`python3 scripts/validate_findings.py`, etc.).

## 3. Entry Criteria

Begin this workflow when any of the following are true:

- User invokes `/HQE targeted <scope>` or `/HQE bug-hunt <scope>`.
- A specific error, stack trace, flaky test, or anomalous behavior has been reported.
- A subsystem changed recently and now exhibits unexpected behavior.
- A regression is suspected in a defined set of files.

## 4. Stop-the-Line Conditions

Immediately halt the bug hunt and invoke [`workflows/incident-response.md`](incident-response.md) if any of the following are found:

- Active credentials, API keys, tokens, or private keys embedded in the hunt scope.
- A critical security vulnerability (e.g., remote code execution, unauthenticated data access) reachable from the targeted code.
- A data-corruption or data-loss path actively triggered by the reported bug.
- Evidence of active exploitation or unauthorized workflow modifications.

Flag the triggering item as `STOP-THE-LINE: [issue]` in the session log and do not proceed with normal artifact generation until incident response is complete.

## 5. Execution Model

### Phase 0: Scope Definition

**Goal**: Lock the boundaries of the hunt so analysis stays focused.

1. **Confirm the exact bounds**: files, functions, classes, tests, configuration, and data inputs.
2. **Record reproduction clues**: verbatim error messages, stack traces, exit codes, environment details, and frequency (always / flaky / under load).
3. **State expected vs. observed behavior** in one or two sentences each.
4. **List initial hypotheses** using 5W1H or CAGEERF.

**Evidence to collect**:
- Written scope statement.
- Reproduction hypothesis list with confidence tags.
- Reference to triggering issue, log, or user report.

**Exit criteria**:
- [ ] Written scope statement and reproduction hypothesis list exist.
- [ ] Scope is small enough to review in detail without triage shortcuts.

### Phase 1: Contextualize

**Goal**: Build a dependency map limited to the hunt boundary.

1. **Read the targeted files** and their direct dependencies (callers, callees, configuration, tests).
2. **Build a dependency map** showing relevant symbols and call relationships.
3. **Identify recent changes** with `git log --oneline -- <scope>`.
4. **Note any generated, vendored, or binary files** in the scope and exclude them from deep logic review unless modified.

**Evidence to collect**:
- Dependency map (symbols, files, call directions).
- List of relevant commits and authors.
- Classification of files as source / generated / vendored / config / test.

**Exit criteria**:
- [ ] Dependency map and list of relevant symbols exist.
- [ ] Recent changes touching the scope are identified.

### Phase 2: Baseline

**Goal**: Establish current behavior and pre-existing failures.

1. **Run the relevant tests**, build commands, lint, or type checks to establish current behavior.
2. **Record pre-existing failures** to avoid misattribution.
3. **Capture environment**: runtime version, dependency versions, and flags.

**Evidence to collect**:
- Baseline log with pass/fail state and command outputs.
- List of pre-existing failures unrelated to the hunt.

**Exit criteria**:
- [ ] Baseline log with pass/fail state and command outputs exists.
- [ ] Pre-existing failures are documented separately from the target symptom.

### Phase 3: Hypothesize

**Goal**: Decompose the defect into competing, testable hypotheses.

1. **Use 5W1H or CAGEERF** to decompose the defect.
2. **Generate at least two competing hypotheses** when the cause is not obvious.
3. **Rank hypotheses** by likelihood based on code proximity, failure signal, and recent changes.
4. **Apply FOCUS** if multiple hypotheses remain plausible.

**Evidence to collect**:
- Ranked hypotheses with supporting and contradicting evidence.
- Confidence tag for each hypothesis.

**Exit criteria**:
- [ ] Ranked hypotheses with supporting and contradicting evidence exist.
- [ ] Each hypothesis is falsifiable with a concrete test or inspection.

### Phase 4: Trace Execution

**Goal**: Follow data flow and control flow for the leading hypotheses.

1. **Trace data flow** from input to the failure site.
2. **Trace control flow** through branching conditions, loops, error handling, and concurrency.
3. **Inspect state transitions** and boundary conditions (null, empty, max length, concurrency).
4. **Record the exact code path** with `file:line` or `anchor+grep`.

**Evidence to collect**:
- Evidence trail linking the symptom to a candidate root cause.
- Verbatim 2–5 line snippets at each key transition.

**Exit criteria**:
- [ ] Evidence trail links the symptom to a candidate root cause.
- [ ] Each transition cites exact file paths and line numbers.

### Phase 5: Validate Hypothesis

**Goal**: Confirm or refute the leading root cause.

1. **Seek static proof**: exact snippet + line numbers showing the defect.
2. **Write a targeted reproduction test** when static proof is insufficient.
3. **Use FOCUS** to eliminate competing hypotheses if multiple remain plausible.
4. **Run the reproduction test** and record the result.

**Evidence to collect**:
- Confirmed or refuted root cause with evidence.
- Reproduction test or static proof artifacts.

**Exit criteria**:
- [ ] A confirmed or refuted root cause with evidence exists.
- [ ] Uncertain root causes are marked `[NEEDS_VERIFICATION]`.

### Phase 6: Fix or Report

**Goal**: Deliver either a remediation patch or a documented finding.

1. **If asked to remediate**, follow [`workflows/remediation-run.md`](remediation-run.md) with a strict change budget.
2. **Otherwise**, emit findings using the standard schema and provide a reproduction case.
3. **Add a regression test** that fails before the fix and passes after it when remediation is performed.
4. **Update the session log** with completed, in-progress, discovered, and reprioritized items.

**Evidence to collect**:
- Remediation patch or documented finding with verification command.
- Regression test with before/after results.

**Exit criteria**:
- [ ] Remediation patch or documented finding with verification command exists.
- [ ] Regression test is added when remediation is performed.

## 6. Required Controls / Checks

- Keep the change budget to `<= 5` files unless the user explicitly approves a larger change.
- Do not perform speculative mass refactors while hunting a bug.
- Every claim must cite exact file paths, line numbers, and 2–5 line snippets.
- Add a regression test that fails before the fix and passes after it when remediation is performed.
- Run tests honestly; never report a test as passing unless it was executed.
- Mark uncertain root causes as `[NEEDS_VERIFICATION]` rather than fabricating a cause.
- Use the **Brief** profile for quick triage and the **Standard** profile when multiple findings emerge.
- Distinguish first-party source from generated, vendored, build, or binary files.

## 7. Artifact Outputs

- `HQE_REPORT.md` (targeted findings and reproduction summary)
- `HQE_FINDINGS.json`
- `HQE_RUN_MANIFEST.json`
- `HQE_SESSION_LOG.json`
- `HQE_PATTERN_FINDINGS.md` (if the hunt reveals recurring anti-patterns)
- `HQE_HANDOFF.md` (when handing off remediation to another agent)

Validate machine-readable artifacts with:

```bash
python3 scripts/validate_findings.py HQE_FINDINGS.json
python3 scripts/validate_manifest.py HQE_RUN_MANIFEST.json
python3 scripts/validate_session_log.py HQE_SESSION_LOG.json
```

## 8. Exit Criteria

The targeted bug hunt is complete when:

- [ ] All phases above have been executed or explicitly skipped with justification.
- [ ] The root cause is confirmed or explicitly marked `[NEEDS_VERIFICATION]`.
- [ ] Every claim cites exact file paths, line numbers, and 2–5 line snippets.
- [ ] A remediation patch or documented finding with verification command exists.
- [ ] Regression test is added when remediation is performed.
- [ ] Artifacts are emitted and schema-validated.
- [ ] Stop-the-line conditions have been checked; if triggered, incident response has been invoked.
- [ ] The session log is updated with completed, in-progress, discovered, and reprioritized items.

## 9. Confidence Model Reminders

Tag every major claim:

- `[FACT]` — Directly observed code, command output, or test result.
- `[INFERENCE]` — Reasonable deduction from direct evidence.
- `[HYPOTHESIS]` — A plausible explanation that requires a discriminating test.
- `[NEEDS_VERIFICATION]` — Not yet proven; must not be presented as the confirmed root cause.

Never claim a bug is fixed until a targeted verification command passes.
