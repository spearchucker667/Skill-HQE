# Workflow: Debug Error & Exception Diagnosis

This workflow defines the systematic, evidence-first protocol for diagnosing runtime exceptions, panics, build failures, or test crashes.

---

## Phase 1: Input & Error Ingestion
1. **Collect Crash Context**:
   - Capture verbatim error message, exit code, and full stack trace.
   - Record operating system, runtime version, environment variables, and active flags.
2. **Identify Top Stack Frames**:
   - Locate first-party codebase frames in the stack trace; filter out third-party/runtime frames.
   - Map filenames and line numbers to exact repository source files.

---

## Phase 2: Frame & State Reconstruction
1. **Source Inspection**:
   - Open source files at the exact line of failure.
   - Inspect 20 lines before and after the failure site.
   - Identify variable states, input parameters, and nullability/bounds assumptions at the site of the crash.
2. **5W1H & Genesis Tracing**:
   - Trace backwards from the crash site to find where invalid state or unhandled data originated.
   - Inspect all intermediate function calls and transformations.

---

## Phase 3: Hypothesis Formulation & Discriminating Proof
1. **Formulate Hypotheses**:
   - Generate explicit, testable hypotheses explaining the failure.
   - Apply the FOCUS framework if multiple causes are plausible.
2. **Construct Tier 2 Reproduction Test**:
   - Write a minimal, deterministic unit test or script that feeds the triggering input to the faulty function.
   - Run the reproduction test to confirm that it fails with the exact observed error.

---

## Phase 4: Minimal Root-Cause Remediation
1. **Apply Change Budget**:
   - Formulate the minimal fix addressing the root cause (target: $\le 2$ files).
   - Ensure edge cases (null values, empty collections, network disconnects) are handled.
2. **Validate Fix**:
   - Run the reproduction test; verify it passes.
   - Run the full test suite to ensure zero regressions.
3. **Document Finding**:
   - Record finding as `HQE-BUG-xxx` in `HQE_FINDINGS.json`.
