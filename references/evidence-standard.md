# Evidence Standard

In HQE, claims without verifiable evidence are considered non-compliant hallucinations.

---

## 1. The Triad of Proof

Every finding reported under the HQE protocol must satisfy the **Triad of Proof**:

1. **Exact Location Anchor**: File path relative to repository root, start line, end line, and surrounding symbol/function name.
2. **Verifiable Code Snippet**: A concise 2–5 line excerpt directly copied from the source demonstrating the defect.
3. **Causal Reasoning / Impact Statement**: Explicit explanation of how the code snippet leads directly to the observed failure or vulnerability.

---

## 2. Snippet Formatting Rules

- Snippets must be exact character-for-character representations of source code.
- Never invent imaginary lines or guess line offsets.
- Always include surrounding context if line numbers alone are ambiguous.

```json
{
  "path": "src/services/billing.ts",
  "start_line": 84,
  "end_line": 87,
  "symbol": "chargeSubscription",
  "snippet": "if (user.isTrialExpired) {\n  await paymentGateway.charge(user.id, plan.amount);\n  user.status = 'ACTIVE';\n}"
}
```
