# Final Quality Gate & Pre-Delivery Audit Workflow

This workflow guides the host AI agent through the final verification pass before publishing audit findings or applying remediations.

---

## 1. Objective
Enforce the definition of done (DoD), pre-delivery checklist, and automated quality gates defined in [`../references/pre-delivery-gates.md`](../references/pre-delivery-gates.md) and [`../references/quality-gates.md`](../references/quality-gates.md).

---

## 2. Gate Verification Checklist

### Gate 1: Evidentiary Proof
- [ ] Every finding has valid line bounds and non-empty code snippet.
- [ ] Snippets are sanitized with zero unredacted secrets.

### Gate 2: Severity & Taint Chain Integrity
- [ ] All `CRITICAL` and `HIGH` findings satisfy severity gates (preconditions, exploitability, blast radius, likelihood).
- [ ] All `SEC` findings have complete source-to-sink taint chains.

### Gate 3: Change Budget & Anti-Regression (Remediation Runs)
- [ ] Modified file count $\le 5$.
- [ ] Any behavioral or dependency change is explicitly flagged with `[BEHAVIOR CHANGE]` or `[NEW_DEPENDENCY]`.
- [ ] Tier 1 verification tests run and passed.

### Gate 4: Artifact Completeness
- [ ] Run manifests, session logs, and audit deliverables pass schema validation:
  ```bash
  python3 scripts/validate_findings.py findings.json
  python3 scripts/validate_semantics.py findings.json
  python3 scripts/validate_manifest.py HQE_RUN_MANIFEST.json
  python3 scripts/validate_session_log.py HQE_SESSION_LOG.json
  ```
