# Full Audit Workflow

The `full` audit workflow is designed for comprehensive repository analysis.

## Execution Model

1. **Phase -1: Change/PR Harvest** (If applicable, read diffs)
2. **Phase 0: Orientation** (Discover languages, frameworks, entrypoints, testing commands)
3. **Phase 0.5: Scope/Triage** (For large repos, build coverage strategy prioritizing boundaries and changed code)
4. **Phase 1: Build/Test/Static Baseline** (Run formatting, linting, tests to establish baseline)
5. **Phase 2: Deep Domain Review**
   - Correctness
   - Reliability
   - Security
   - Performance
   - Architecture
   - Tests
   - CI/CD
   - Dependencies
   - Documentation / DX / UX
6. **Phase 3: Cross-Cutting Analysis** (Trace issues across modules)
7. **Phase 4: Reproduction/Validation** (Establish confidence level for major bugs)
8. **Phase 5: Finding Consolidation** (Deduplicate by root cause)
9. **Phase 6: Prioritization** (Rank by severity, impact, effort)
10. **Phase 7: Remediation Planning** (Determine root cause, target files, minimal safe fix)
11. **Phase 10: Artifact Generation** (Assemble explicit protocol artifacts)

## Output Format
Use the Exhaustive output profile, which emits the following artifacts:
- `HQE_REPORT.md` (Executive summary, methodologies, high-level findings)
- `HQE_FINDINGS.json` (Machine-readable findings list)
- `HQE_RUN_MANIFEST.json` (Coverage, mode, subsystem counts, and health score)
- `HQE_RISK_REGISTER.md`
- `HQE_MASTER_TODO.md`
- `HQE_PATTERN_FINDINGS.md`
- `HQE_SECURITY_POSTURE.md`
- `HQE_RELIABILITY.md`
- `HQE_TESTING_GAPS.md`
- `HQE_UNKNOWNS.md`
- `HQE_CONFIDENCE.md`
- `HQE_SESSION_LOG.json`
- `HQE_HANDOFF.md` (When requested for implementation handoff)
