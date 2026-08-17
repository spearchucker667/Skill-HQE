# HQE Skill Parity Repair — Agent Launch Handoff

## Mission

Repair and extend:

```text
/Users/super_user/Projects/Skill-HQE/
```

using the actual HQE implementation and protocol at:

```text
/Users/super_user/Projects/HQE-Workbench/
```

The objective is not to recreate HQE Workbench. Restore the HQE-specific engineering capabilities that were lost or weakened during conversion while preserving the skill-native `/HQE` architecture.

Use the accompanying:

```text
HQE_SKILL_PARITY_REPAIR_AGENT_HANDOFF.md
```

as the authoritative detailed implementation specification.

## Highest-Priority Work

Restore the actual HQE protocol control plane:

```text
health scoring
severity gates
likelihood/exposure justification
trust-boundary analysis
security taint chains
change budgets
anti-regression / BEHAVIOR CHANGE rules
stop-the-line incident handling
no-stall blocker instrumentation
reproducibility manifests
output controls
patch packaging
session logging
quality gates
definition of done
pre-delivery checks
```

Restore the canonical HQE artifact system, including the Risk Register, Master TODO Backlog, Pattern Findings, Quick Wins vs Structural Work, Security Posture Summary, Reliability Summary, Testing Gaps, Unknowns & Verification, Confidence Declaration, run manifest, session log, and redaction log.

Fix the current implementation defects, especially:

```text
SKILL.md Phase -1 / Phase 0 ordering conflict
NEEDS_VERIFICATION vocabulary mismatch
broken README protocol link
broken docs/ -> references/ Markdown links
false "complete HQE v4.2.1" claims
nonexistent redaction-engine claims
non-guaranteed sandbox claims
overbroad zero-telemetry guarantees
weak check_skill.py
fail-open validate_findings.py
deprecated RefResolver usage
underconstrained finding schema
underconstrained run-manifest schema
underconstrained handoff schema
inventory_repo.py coverage undercounting
detect_manifests.py silent truncation/incomplete ecosystems
missing test-command detection
release archive debris
```

Restore missing dedicated references and workflows for:

```text
testing
dependencies
CI/CD
documentation
UX/DX
boot/startup
technical debt
observability
security
architecture
performance
regression analysis
incident response
verification
```

Mine and selectively translate the useful engineering portions of:

```text
mcp-server/code-review.toml
mcp-server/criticalthink/
mcp-server/conductor/
mcp-server/cli-security/
mcp-server/cli-prompt-library/
mcp-server/prompts/server/resources/gates/
mcp-server/prompts/server/resources/methodologies/
```

Do not port the MCP runtime wholesale.

Restore safe local capabilities derived from HQE Workbench:

```text
scripts/redact_secrets.py
scripts/local_risk_scan.py
scripts/detect_test_commands.py
scripts/validate_manifest.py
scripts/validate_semantics.py
scripts/summarize_tree.py
```

Strengthen testing so a successful test run actually proves HQE integrity rather than merely file existence. Add schema coherence tests, helper behavior tests, Markdown link tests, redaction tests, packaging tests, and acceptance fixtures for Rust, TypeScript, broken CI, security boundaries, malicious prompt injection, dirty working trees, incomplete context, and large repositories.

Do not declare completion until `/HQE` can demonstrate source-to-skill parity through `docs/CAPABILITY_MAPPING.md`, the expanded test suite, and representative acceptance scenarios.

Do not recreate the desktop application, provider UI, encrypted database, Keychain layer, Tauri/React interface, vector runtime, or MCP transport server unless a specific component is independently useful to the skill.

Do not blindly copy source material. Review licensing and source lineage, particularly the Apache 2.0 repository license versus MIT metadata present in the HQE protocol.

At completion, report every capability ported, translated, intentionally dropped, every bug fixed, every validation command executed, exact test results, remaining limitations, and the final clean skill tree.
