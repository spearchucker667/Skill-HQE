# Educational Clarity Gate

> **Source lineage:** HQE-Workbench `mcp-server/prompts/server/resources/gates/educational-clarity/`. Paraphrased for HQE Skill use.

## Purpose / When to Activate

The Educational Clarity gate ensures that instructional content is pedagogically sound and accessible to the target learner. Activate it for tutorials, guides, onboarding docs, explanations, and any material whose goal is to teach.

## Pass Criteria

- Learning objectives or goals are stated up front.
- Complexity progresses from simple to advanced.
- Abstract concepts include concrete examples.
- Processes are explained step by step.
- Analogies and metaphors aid understanding.
- Practice exercises or applications are included when useful.
- Common misconceptions are anticipated and addressed.
- Jargon is minimized; technical terms are defined.
- Content flows logically with clear transitions.
- A summary or key takeaways section is included.

## Forbidden Patterns / Failure Modes

| Pattern | Risk |
| :--- | :--- |
| Missing learning objectives | Readers do not know what to expect. |
| Sudden jumps in complexity | Cognitive overload. |
| Abstract explanations without examples | Concepts remain inaccessible. |
| Undefined jargon | Novice readers are excluded. |
| No practice or verification step | Learners cannot confirm understanding. |

## Activation Rules

- **Artifact types:** tutorials, educational docs, onboarding guides, explanations.
- **Workflow triggers:** education, documentation, content processing, development training.
- **Explicit request:** not required.

## Retry / Escalation Guidance

1. **First failure:** Add objectives, examples, and a summary.
2. **Second failure (max 2 attempts):** Re-sequence content from concrete to abstract and add a worked example.
3. If the audience is mixed, provide a prerequisites section and optional deeper dives.
