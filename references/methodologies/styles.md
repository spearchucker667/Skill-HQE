> **Source lineage:** HQE-Workbench `mcp-server/prompts/server/resources/styles/`. Paraphrased for HQE Skill use.

# Response Styles

Workbench defines four response styles that shape how a methodology is presented. A style is not a methodology by itself; it is a tone and structure layer that can be applied on top of CAGEERF, ReACT, 5W1H, SCAMPER, FOCUS, or plain tasks.

---

## Analytical

**Purpose:** Produce systematic, data-driven, evidence-based responses.

**When to use:** Analysis, research, debugging, investigations.

**Compatible frameworks:** CAGEERF, ReACT, 5W1H.

**Guidance:** Structure the response with clear sections, present evidence explicitly, and organize findings logically. Prioritize facts over opinion and cite sources or repository artifacts.

---

## Creative

**Purpose:** Encourage unconventional solutions and brainstorming.

**When to use:** Ideation, design exploration, innovation tasks, option generation.

**Compatible frameworks:** SCAMPER, CAGEERF.

**Guidance:** Explore alternatives, brainstorm freely, and encourage novel perspectives. Avoid premature convergence; generate multiple options before evaluating them.

---

## Procedural

**Purpose:** Deliver step-by-step, actionable instructions.

**When to use:** Tutorials, setup guides, installation steps, workflows.

**Compatible frameworks:** CAGEERF, ReACT.

**Guidance:** Number each step, explain prerequisites, and include verification points. Focus on commands and checks the reader can execute.

---

## Reasoning

**Purpose:** Make reasoning explicit and assumptions transparent.

**When to use:** Logic problems, decision evaluation, problem-solving, architecture trade-offs.

**Compatible frameworks:** ReACT, CAGEERF, 5W1H.

**Guidance:** Break down the problem, show the reasoning chain, identify assumptions, and evaluate conclusions systematically. Make the path from premise to conclusion inspectable.

---

## Applying Styles in an HQE Workflow

1. Select the methodology that matches the task structure.
2. Select the style that matches the audience and desired output.
3. Add the style guidance to the system prompt or invocation.
4. Use [Framework Compliance](../gates/framework-compliance.md) to verify that the output follows the methodology and style.
