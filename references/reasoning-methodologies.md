# HQE Reasoning Methodologies & Heuristics

This reference codifies structured analytical frameworks from HQE Workbench for investigating complex bugs, evaluating competing hypotheses, and designing robust remediations without falling into confirmation bias.

---

## 1. 5W1H Analysis (Defect Decomposition)
Use when dissecting ambiguous bug reports or obscure system failures:
- **Who:** Which component, module, or user role triggers the anomaly?
- **What:** What is the exact divergence between observed behavior and expected contract?
- **Where:** What is the precise code path, stack frame, or state transition where corruption begins?
- **When:** Under what timing constraints, lifecycle phase, or concurrency sequence does it occur?
- **Why:** What root architectural or logical assumption was violated?
- **How:** How can the defect be deterministically reproduced in an isolated test fixture?

---

## 2. CAGEERF (Deep Root-Cause Tracing)
- **C - Context:** Establish system preconditions, runtime configuration, and environment flags.
- **A - Anomaly:** Document the exact failure symptom (panic, exception, deadlock, data drift).
- **G - Genesis:** Trace back to the exact code mutation or external input that initiated the faulty state.
- **E - Evolution:** Follow the progression of invalid data through the system pipeline.
- **E - Effect:** Map the blast radius and side-effects across components.
- **R - Root Cause:** Isolate the fundamental flaw (e.g. missing lock, unvalidated cast, off-by-one).
- **F - Fix:** Design a minimal, targeted patch that addresses the genesis while preventing regression.

---

## 3. FOCUS (Competing Hypotheses Disambiguation)
Use when multiple plausible root causes exist:
- **F - Frame:** Explicitly list all competing hypotheses $H_1, H_2, \dots, H_n$.
- **O - Observe:** Collect objective repository evidence and runtime telemetry.
- **C - Compare:** Matrix hypotheses against facts; eliminate hypotheses contradicted by hard evidence.
- **U - Unify:** Determine if remaining hypotheses share a common underlying defect.
- **S - Select & Prove:** Select the highest-probability hypothesis and write a discriminating test to confirm or refute it.

---

## 4. REACT (Incident Response & Triage)
Use during active incidents or high-severity vulnerabilities:
- **R - Recognize:** Identify stop-the-line triggers (leaked credentials, remote exploit path, data corruption).
- **E - Evaluate:** Measure blast radius and exposure depth.
- **A - Act (Contain):** Halt audit pipeline, formulate immediate containment (key revocation, disabling endpoint).
- **C - Check:** Verify that containment is active and no secondary compromise paths remain.
- **T - Track:** Log all indicators of compromise (IoCs), root causes, and remediation steps in `templates/incident-mini-report.md`.

---

## 5. SCAMPER (Remediation Design Options)
Use when evaluating alternative architectural solutions for a tricky bug:
- **S - Substitute:** Can a safer library, data structure, or primitive be substituted?
- **C - Combine:** Can redundant validation boundaries or transformations be combined?
- **A - Adapt:** Can an established design pattern (e.g. state machine, circuit breaker) solve this cleanly?
- **M - Modify/Minimize:** How can the change budget be minimized while preserving correct behavior?
- **P - Put to Another Use:** Can existing test infrastructure or middleware be reused for verification?
- **E - Eliminate:** Can the dead/fragile code path be eliminated entirely?
- **R - Reverse/Rearrange:** Can execution order or async sequencing be rearranged to avoid the hazard?
