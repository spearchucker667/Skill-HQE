# Security Review and Taint Chain

Security findings must trace:
`Source -> Transform(s) -> Validation Boundary -> Sink -> Impact`

For CRITICAL/HIGH severity:
- Require exposure evidence
- Require preconditions
- Require blast radius
- Require exploitability assessment
- Require likelihood
- Downgrade or mark NEEDS_VERIFICATION if exposure cannot be established.
