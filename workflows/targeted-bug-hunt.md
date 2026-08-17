# Targeted Bug Hunt Workflow

When requested (`/HQE targeted`), focus deeply on a specific issue, file, or subsystem.

## Execution Model
1. **Define Scope**: Explicitly clarify the bounds of the hunt.
2. **Contextualize**: Read the targeted files and their direct dependencies.
3. **Hypothesize**: Formulate hypotheses about the bug's root cause.
4. **Trace Execution**: Follow the data flow and control flow related to the hypotheses.
5. **Validate Hypothesis**: Look for static evidence or write a targeted reproduction case.
6. **Report**: Output the specific findings using the standard schema.
