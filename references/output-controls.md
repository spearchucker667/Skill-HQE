# HQE Output Controls & Cap Management

This reference defines how HQE manages token budgets, artifact output volumes, and finding prioritization to prevent noisy, low-value information dumps while guaranteeing that critical issues are never hidden.

---

## 1. Core Principles

1. **Never Suppress Criticality**: A CRITICAL or HIGH severity finding is NEVER suppressed due to output caps.
2. **Consolidate Low-Severity Noise**: When dozens of low-severity findings share a common root cause or pattern (e.g., missing docstrings or minor lint issues), synthesize them into a single `HQE_PATTERN_FINDINGS.md` entry.
3. **Qualitative & Concrete Coverage**: Never fabricate percentage coverage metrics (e.g. "87.4% covered"). Report qualitative bands (`HIGH`, `MEDIUM`, `LOW`, `UNKNOWN`) accompanied by exact file and line counts.
4. **Explicit Overflow Accounting**: When output caps are triggered, explicitly declare the number of truncated/summarized items and provide filtering criteria to inspect them in subsequent runs.

---

## 2. Output Profiles

| Profile | Target Context | Delivered Artifacts |
| :--- | :--- | :--- |
| **Brief** | PR review, single-issue remediation | Summary report, primary finding(s), verification command |
| **Standard** | Targeted bug hunt, subsystem audit | `REPORT.md`, `HQE_FINDINGS.json`, `HQE_RUN_MANIFEST.json`, `HQE_SESSION_LOG.json` |
| **Exhaustive** | Full repository audit | All 14 canonical Markdown artifacts + `REPORT.md`, `REPORT.json`, `HQE_FINDINGS.json`, `HQE_RUN_MANIFEST.json`, `HQE_SESSION_LOG.json` |

---

## 3. Finding Caps & Overflow Thresholds

For standard and exhaustive runs:
- **CRITICAL / HIGH Findings**: Uncapped. All valid CRITICAL/HIGH findings must be reported in full detail with severity gates.
- **MEDIUM Findings**: Default cap of 15 individual findings per category. If more exist, the top 15 by risk score are detailed, and remainder are grouped into systemic patterns.
- **LOW / INFO Findings**: Default cap of 10 individual findings. Remainder are aggregated into the TODO backlog and pattern findings.

### Overflow Declaration Format
When findings exceed profile thresholds, include an overflow banner:

```markdown
> [!NOTE]
> **Output Cap Applied**: 18 MEDIUM findings detected; top 15 detailed above. 3 additional findings consolidated under `HQE-DEBT-009 (Systemic Logging Inconsistencies)`.
```

---

## 4. Chunking & Large Repository Context Strategy

For repositories exceeding 50 source files or 100,000 LOC:
- **Subsystem Partitioning**: Group files into logical subsystems (e.g. `core/`, `api/`, `auth/`, `frontend/`, `cli/`).
- **Ledger-Driven Tracking**: Record reviewed chunks in `HQE_RUN_MANIFEST.json` under `coverage.deep_reviewed` and `coverage.skipped`.
- **Stateless Continuity**: Each chunk scan updates the persistent `HQE_SESSION_LOG.json` to allow multi-turn audit execution without losing previous findings.
