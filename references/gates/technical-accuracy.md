# Technical Accuracy Gate

> **Source lineage:** HQE-Workbench `mcp-server/prompts/server/resources/gates/technical-accuracy/`. Paraphrased for HQE Skill use.

## Purpose / When to Activate

The Technical Accuracy gate verifies that technical claims, version references, and specifications are correct and grounded in evidence. Activate it for documentation, research summaries, analysis reports, and any output that cites standards, RFCs, or library versions.

## Pass Criteria

- Technical facts are verified before being stated.
- Terminology is precise and used correctly.
- Version numbers and compatibility notes are included where relevant.
- A distinction is made between stable and experimental features.
- Technical decisions include context and trade-offs.
- Official documentation is referenced when available.
- Code examples are syntactically correct and include error handling.

## Forbidden Patterns / Failure Modes

| Pattern | Risk |
| :--- | :--- |
| Unverified claims presented as facts | Misleading guidance or incorrect remediation. |
| Missing version context | Incompatible advice for the target runtime. |
| Vague terminology | Ambiguous instructions and integration errors. |
| Speculation about implementation | Advice based on assumptions rather than evidence. |
| Code examples with syntax errors | Non-functional remediation steps. |

## Activation Rules

- **Artifact types:** technical documentation, research reports, analysis outputs, API references.
- **Workflow triggers:** analysis, research, development guidance.
- **Explicit request:** required; this gate should be requested for high-stakes technical summaries.

## Retry / Escalation Guidance

1. **First failure:** Re-check cited facts against official documentation or repository artifacts.
2. **Second failure:** Add `[NEEDS_VERIFICATION]` markers to uncertain claims and downgrade confidence.
3. **Third failure (max 3 attempts):** Escalate to a human reviewer or run the repository's own test/typecheck commands as a ground-truth oracle.
