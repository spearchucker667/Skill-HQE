# HQE Audit Methodology

**Protocol Version**: HQE Protocol v5.0.0

The HQE audit methodology is designed to replace superficial pattern matching with deep, evidence-based systems engineering.

---

## 1. Core Execution Phases

```
[Phase 0: Orientation] -> [Phase 1: Baseline] -> [Phase 2: Domain Deep-Dive]
          -> [Phase 3: Cross-Cutting Synthesis] -> [Phase 4: Validation] -> [Phase 5: Artifacts]
```

### Phase 0: Orientation & Ingestion Filter
1. Discover project type, manifests, languages, entrypoints, and test setups.
2. Build initial repository map and coverage strategy.
3. Establish exclusion rules for generated or vendored assets.

### Phase 1: Baseline Verification
1. Run formatting, linting, typechecking, and tests to establish the baseline health.
2. Record pre-existing failures to avoid attributing legacy issues to current work.

### Phase 2: Domain Deep-Dive
Systematically analyze across key dimensions:
- **Correctness**: Invariants, data integrity, edge cases.
- **Security**: Attack surfaces, trust boundaries, injection vectors, credentials.
- **Reliability**: Race conditions, deadlocks, error handling, retries, failovers.
- **Performance**: Algorithmic complexity, hot-path I/O, cache utilization.
- **Architecture**: Module coupling, boundary leaks, abstraction clarity.
- **CI/CD & Dependencies**: Supply-chain vulnerabilities, build pipeline fragility.

### Phase 3: Cross-Cutting Synthesis
Correlate findings across multiple files. Group related symptoms into unified root-cause issues.

### Phase 4: Dynamic Validation & Reproduction
Establish reproduction steps or proof cases for all `CRITICAL` and `HIGH` findings.

### Phase 5: Artifact Production
Produce the structured `HQE_REPORT.md` and `HQE_FINDINGS.json`.
