# ReACT Methodology

> **Source lineage:** HQE-Workbench `mcp-server/prompts/server/resources/methodologies/react/`. Paraphrased for HQE Skill use.

## Purpose

ReACT is an iterative reasoning-and-action methodology. It forces explicit reasoning before action, then observes the results of those actions and adjusts the approach accordingly. It is well suited to dynamic problem-solving where feedback is available after each step.

Use ReACT for interactive debugging, adaptive remediation, tool-driven investigations, and any task where the next step depends on the outcome of the previous one.

## Phases / Steps

| Phase | Question to Answer | Required |
| :--- | :--- | :--- |
| **Reason** | What is the systematic analysis and planned approach? | Yes |
| **Act** | What specific, purposeful action is taken? | Yes |
| **Observe** | What are the results, feedback, and outcomes? | Yes |
| **Adjust** | How should reasoning and approach change based on observations? | Optional |
| **Continue** | Should the cycle repeat or is the objective achieved? | Optional |

Execution dependencies flow: Reason → Act → Observe → Adjust → Continue, with cycles repeating until the objective is met.

## Judge-Prompt Guidance

When reviewing a ReACT-shaped artifact, verify:

1. **Reasoning quality** — problem analysis is systematic, explicit, and traceable.
2. **Action specificity** — actions are concrete, purposeful, and measurable.
3. **Observation completeness** — results are analyzed thoroughly against objectives.
4. **Cycle effectiveness** — adjustments are based on observations and progress is evident.
5. **Termination clarity** — it is clear when and why the cycle stops.

## Compatible Frameworks / Styles

- **Compatible styles:** reasoning, procedural, analytical.
- **Matching gate:** `references/gates/framework-compliance.md`.
- **Often paired with:** [Technical Accuracy](../gates/technical-accuracy.md), [Test Coverage](../gates/test-coverage.md).

## Example Usage in an HQE Workflow

During an **interactive debugging session**, apply ReACT as follows:

- **Reason:** Hypothesize that a flaky test is caused by a race condition.
- **Act:** Add logging around the suspected critical section and run the test suite.
- **Observe:** Review logs for interleaving patterns and failure frequency.
- **Adjust:** If logs confirm the race, add synchronization; if not, form a new hypothesis.
- **Continue:** Repeat until the test is stable and a regression test is added.

Record each cycle in the session log and attach the final regression test as evidence.
