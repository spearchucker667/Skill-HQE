# Provider-Independent Review Workflow

This workflow ensures that HQE audits are performed consistently and deterministically, regardless of the underlying AI provider (e.g., Gemini, Claude, OpenAI) executing the skill. It mandates evidence-based reasoning over provider-specific heuristics.

---

## 1. Grounding in Raw Evidence
**Principle:** Do not rely on internal model knowledge for repository-specific context.
**Actions:**
- Always extract actual code snippets, configuration files, and build outputs using standard file reading tools.
- Cite specific line numbers and file paths when discussing a finding.
- Validate assumptions by running tests or executing search queries against the repository.

## 2. Standardized Artifact Generation
**Principle:** Outputs must conform strictly to HQE schemas and templates.
**Actions:**
- Use the defined JSON schemas (e.g., `schemas/finding.schema.json`) for machine-readable output.
- Use the markdown templates (e.g., `templates/finding.md`) for human-readable reports.
- Avoid provider-specific formatting quirks (e.g., excessive conversational filler or non-standard markdown structures).

## 3. Explicit Confidence Declarations
**Principle:** Distinguish between facts, inferences, and hypotheses.
**Actions:**
- Tag every major claim with a confidence level: `FACT`, `INFERENCE`, `HYPOTHESIS`, or `NEEDS_VERIFICATION`.
- Never present an unverified inference or hypothesis as a definitive fact.
- If a provider's internal reasoning leads to a conclusion, it must be backed by verifiable repository evidence.

## 4. Deterministic Taint Chains
**Principle:** Security findings must follow a rigid structural logic.
**Actions:**
- For any vulnerability, map the exact flow: `Source -> Transform -> Validation -> Sink`.
- If a step in the chain cannot be proven with code, the finding must be marked `NEEDS_VERIFICATION`.

## 5. Agnostic Remediation Planning
**Principle:** Proposed fixes should be idiomatic to the language and framework, not biased by the AI's preferred patterns.
**Actions:**
- Reference the project's existing coding standards and dependencies when suggesting a patch.
- Provide minimal, targeted diffs rather than full-file rewrites.
- Ensure the remediation is verifiable through the project's testing infrastructure.
