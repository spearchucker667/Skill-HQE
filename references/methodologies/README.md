# HQE Workbench Methodologies

This directory contains portable reference definitions for the structured methodologies defined in HQE Workbench's prompt resource library. Each methodology provides a reusable thinking framework that can be applied to analysis, planning, creative problem-solving, or incident response.

> **Source lineage:** HQE-Workbench `mcp-server/prompts/server/resources/methodologies/`. These references paraphrase the original machine-readable methodology definitions; see `references/source-lineage.md` for provenance.

---

## Methodology Index

| Methodology | ID | Best For |
| :--- | :--- | :--- |
| [CAGEERF](cageerf.md) | `cageerf` | End-to-end problem solving, from context gathering through execution and refinement. |
| [FOCUS](focus.md) | `focus` | Focused problem-solving, solution design, and implementation. |
| [5W1H](5w1h.md) | `5w1h` | Comprehensive requirement gathering and stakeholder analysis. |
| ReACT (`react.md`) | `react` | Iterative reasoning-action cycles and adaptive problem-solving. |
| SCAMPER (`scamper.md`) | `scamper` | Creative ideation, innovation, and alternative solution generation. |
| [Critical Thinking](critical-think.md) | `critical-think` | Stress-testing assumptions, evidence, and conclusions before delivery. |
| [Code Review](code-review.md) | `code-review` | Structured source-code evaluation mapped to HQE finding categories. |

---

## Response Styles

Workbench also defines four response styles that can be layered onto any methodology. See `styles.md` for details.

- **Analytical** — data-driven, logical, evidence-based.
- **Creative** — unconventional, brainstorming, ideation-friendly.
- **Procedural** — step-by-step, tutorial-like, verification-oriented.
- **Reasoning** — explicit reasoning chains, assumption tracking.

---

## Selecting a Methodology

1. Clarify the task type (analysis, planning, creative exploration, incident response).
2. Choose the methodology whose phases match the mental model you want to enforce.
3. Pair it with a compatible response style from `styles.md`.
4. Apply the matching gate from `references/gates/framework-compliance.md` to verify phase coverage.
