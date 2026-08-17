# Content Structure Gate

> **Source lineage:** HQE-Workbench `mcp-server/prompts/server/resources/gates/content-structure/`. Paraphrased for HQE Skill use.

## Purpose / When to Activate

The Content Structure gate ensures that prose artifacts are well organized, readable, and easy to navigate. Activate it for documentation, analysis reports, educational material, research summaries, and general written output.

## Pass Criteria

- Clear headings and subheadings structure the document.
- Content is organized in logical sections.
- Bullet points or numbered lists improve scannability.
- Examples are provided when explaining concepts.
- Tone and style are consistent throughout.
- Sections transition smoothly.
- A summary or conclusion is included when appropriate.

## Forbidden Patterns / Failure Modes

| Pattern | Risk |
| :--- | :--- |
| Wall of text without headings | Readers cannot locate information. |
| Inconsistent heading levels | Confusing hierarchy. |
| Missing lists or examples | Abstract concepts remain unclear. |
| Abrupt section jumps | Disorienting narrative. |
| No conclusion | Readers miss key takeaways. |

## Activation Rules

- **Artifact types:** Markdown documents, reports, guides, research summaries, educational content.
- **Workflow triggers:** documentation, content processing, education, analysis, research, general writing.
- **Explicit request:** not required.

## Retry / Escalation Guidance

1. **First failure:** Add headings, lists, and a conclusion.
2. **Second failure (max 2 attempts):** Re-outline the document before rewriting, ensuring each section has a single responsibility.
3. For long documents, add a table of contents and anchor links.
