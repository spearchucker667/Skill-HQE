# HQE Engineer Protocol v5.0.0 Migration Notes

HQE v5.0.0 consolidates the protocol around a single engineering control plane.

Changes:
- YAML remains the source of truth.
- Schemas are aligned to v5.0.0.
- Security, evidence, regression, and delivery controls are explicit.
- Findings support lifecycle tracking.
- Artifact expectations are machine-readable.

Validation:

```bash
python3 protocol/validate.py protocol/hqe-engineer.yaml
python3 protocol/verify.py --verbose
```
