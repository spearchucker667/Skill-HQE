# Critical Thinking & Critique Rubric

> **Source lineage:** HQE Workbench critical-inquiry practices. Adapted for HQE Skill audits where assumptions, conclusions, and evidence must be stress-tested before delivery.

## Purpose

The Critical Thinking rubric is a disciplined critique framework for HQE audits. It forces the reviewer to separate observations from inferences, surface hidden assumptions, and verify that every finding is justified by repository evidence rather than pattern matching or authority.

Use this methodology when an audit artifact feels too clean, when findings cluster around obvious symptoms, or before finalizing a report that will drive remediation decisions.

## When to Activate

- Before signing off on a set of findings that will be handed to remediation.
- When severity or confidence escalations are requested.
- When multiple reviewers disagree on root cause or impact.
- When an audit scope is broad and findings may be under-specified.
- When repository content (README, comments, AGENTS.md) contains claims that could be mistaken for evidence.

## Pass Criteria

1. **Evidence is primary** — every claim can be traced to a file path, line number, command output, or test result.
2. **Assumptions are explicit** — unstated premises are written down and labeled `[ASSUMPTION]`.
3. **Alternative explanations are considered** — at least one competing hypothesis is documented for non-trivial findings.
4. **Severity is proportional** — impact statements match the actual blast radius, not the worst imaginable scenario.
5. **Confidence labels are defensible** — `FACT`, `INFERENCE`, `HYPOTHESIS`, and `NEEDS_VERIFICATION` are applied consistently.
6. **No category errors** — findings are classified against the correct HQE category (`BOOT`, `SEC`, `BUG`, `REL`, `PERF`, `UX`, `DX`, `DOC`, `DEBT`, `DEPS`).
7. **Conclusions are actionable** — remediation steps are concrete and validated by at least one verification command.

## Red Flags

| Red flag | Risk | Response |
| :--- | :--- | :--- |
| Findings cite documentation instead of code | Authority bias; the README may be stale or wrong. | Re-anchor to source or downgrade confidence. |
| Every issue is HIGH or CRITICAL | Severity inflation reduces trust and prioritization accuracy. | Re-evaluate each against the severity gate in `schemas/finding.schema.json`. |
| No `NEEDS_VERIFICATION` items | Overconfidence; complex audits always have gaps. | Identify at least one unresolved question per subsystem. |
| Root cause stops at the first plausible explanation | Symptom-level fixes and missed structural issues. | Apply 5 Whys or CAGEERF before finalizing. |
| Remediation lacks verification | Fixes cannot be proven to work. | Add a command or test that demonstrates resolution. |
| Claims use absolute language (`will`, `must`) without proof | Rhetorical certainty masks weak evidence. | Replace with likelihood-qualified statements. |

## Example Questions

Use these questions during critique passes:

- What would falsify this finding? Can I construct a counter-example from the code?
- Is the evidence sufficient to support the confidence label, or should it be downgraded?
- What audience does this finding serve? Does the impact statement match their concerns?
- Have I confused correlation with causation in the root-cause chain?
- Would another maintainer reach the same conclusion from the same evidence?
- Are there legitimate reasons the existing code was written this way? What constraints did the author face?
- Does the remediation introduce new risks, dependencies, or behavior changes?
- If this finding is wrong, what is the cost of acting on it?

## Compatible Frameworks / Styles

- **Compatible styles:** analytical, reasoning.
- **Often paired with:** [CAGEERF](cageerf.md), [5W1H](5w1h.md), [FOCUS](focus.md).
- **Matching gate:** `references/gates/technical-accuracy.md`.

## Example Usage in an HQE Workflow

During the final consolidation of a **full audit**, apply the Critical Thinking rubric to each HIGH or CRITICAL finding:

1. Re-read the evidence snippet in its original context.
2. List the assumptions required for the finding to hold.
3. Construct one alternative explanation and state what evidence would decide between them.
4. Verify the severity gate fields (`preconditions`, `exploitability`, `blast_radius`, `likelihood`, `exposure_evidence`) are populated and justified.
5. Adjust confidence or severity before publishing the finding.

Output the critique notes as an appendix in `HQE_CONFIDENCE.md` or inline in the finding justification.
