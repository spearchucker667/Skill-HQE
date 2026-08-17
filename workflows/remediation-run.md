# Remediation Run Workflow

When requested (`/HQE remediate`), execute fixes for known findings.

## Execution Model
1. **Ingest Handoff**: If provided an HQE Handoff document, read it carefully.
2. **Re-Verify Context**: Ensure the findings still apply to the current code state.
3. **Plan Minimal Fixes**: Adhere strictly to the minimal-change bias.
4. **Iterative Execution**: 
   - Apply fix for Finding 1.
   - Run relevant validation tests.
   - Proceed to Finding 2.
5. **Document Outcomes**: Record which findings were successfully fixed and verified, and which failed.
