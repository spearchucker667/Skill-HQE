# HQE Escalation Patterns

This reference defines the structured escalation paths for findings during an HQE audit. When an agent discovers a vulnerability or defect, it must follow these patterns to ensure appropriate triage, containment, and reporting.

---

## 1. Zero-Day / Critical Vulnerability Escalation
**Trigger:** Discovery of an unauthenticated remote code execution (RCE), exposed high-privilege credentials, or massive data exfiltration path.
**Action:**
- **Halt Routine Audit:** Stop broad repository scanning to prevent tipping off adversaries or causing accidental triggers.
- **Isolate Evidence:** Capture the specific lines of code, configuration, or payload that demonstrate the vulnerability without executing destructive actions.
- **Generate Incident Report:** Immediately populate `templates/incident-mini-report.md`.
- **Notify:** Output a high-priority alert to the user detailing the blast radius and required immediate containment.

## 2. Systemic Architectural Flaw Escalation
**Trigger:** Discovery of a fundamental design flaw that affects multiple components (e.g., lack of centralized authentication, improper use of a database resulting in N+1 queries everywhere).
**Action:**
- **Document Pattern:** Instead of reporting hundreds of individual instances, document the root architectural failure in `HQE_PATTERN_FINDINGS.md`.
- **Provide Exemplar:** Select one or two clear examples to illustrate the flaw.
- **Recommend Structural Fix:** Propose a systemic remediation (e.g., introducing a middleware layer or changing a library) rather than localized patches.

## 3. High-Friction Developer Experience Escalation
**Trigger:** Identification of severely degraded DX, such as broken build scripts, excessively slow tests, or convoluted deployment processes.
**Action:**
- **Capture Impact:** Measure or estimate the time lost due to the friction.
- **Escalate to `HQE_RELIABILITY.md`:** Log the issue as a systemic reliability or productivity blocker.
- **Prioritize Fix:** If the fix is small (a "quick win"), generate a patch. Otherwise, document it in the Master TODO backlog.

## 4. Ambiguous Intent Escalation
**Trigger:** Encountering code where the developer's intent is completely unclear, and modifying it carries high risk of regression.
**Action:**
- **Classify as Unknown:** Add the component to `HQE_UNKNOWNS.md`.
- **Request Human Review:** Formulate specific questions for the user to clarify the intended behavior.
- **Isolate:** Do not attempt to refactor or "fix" the code without confirmation.

## 5. Security Boundary Escalation
**Trigger:** Identifying a lack of clear separation between trusted and untrusted components.
**Action:**
- **Map Taint Chain:** Explicitly trace the flow of untrusted data.
- **Propose Boundary:** Suggest the introduction of a validation layer or sanitization routine.
- **Elevate Severity:** If the boundary failure leads directly to a sink, escalate the finding to HIGH or CRITICAL depending on impact.
