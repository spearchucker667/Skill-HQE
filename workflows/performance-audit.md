# Performance Audit Workflow

The `performance` audit workflow (`/HQE performance`) profiles hot paths, identifies bottlenecks, and evaluates concurrency, allocation, and I/O behavior.

## Objective

Find evidence-based performance defects and optimization opportunities. Prioritize issues by real impact on hot paths rather than micro-optimizations. Never invent metrics; report qualitative bands backed by line anchors and, when available, reproducible measurements.

## Trigger Conditions

- User invokes `/HQE performance`.
- Latency, throughput, or resource-utilization regressions are reported.
- The system is approaching a scale milestone or load target.
- A recent change introduced suspicious complexity, blocking I/O, or memory growth.
- Profiling data, load tests, or production telemetry indicate a bottleneck.

## Execution Model

1. **Phase 0: Orientation & Hot-Path Identification**
   - Discover entrypoints (HTTP endpoints, event handlers, background jobs, CLI commands).
   - Identify loops, recursive paths, database queries, cache interactions, and external calls.
   - **Exit criteria**: Ranked list of hot paths and unbounded input surfaces.

2. **Phase 1: Baseline & Instrumentation**
   - Run existing tests and, when safe, profiling or load-generation commands.
   - Record baseline behavior, including any pre-existing failures.
   - **Exit criteria**: Baseline metrics or a statement that profiling is unavailable.

3. **Phase 2: Algorithmic Complexity**
   - Inspect hot paths for accidental `O(N^2)` or worse complexity on unbounded inputs.
   - Check nested loops, recursive explosion, and combinatorial path growth.
   - **Exit criteria**: Complexity findings with input-size bounds.

4. **Phase 3: I/O & Network Bottlenecks**
   - Look for N+1 query problems, unbatched external calls, synchronous disk I/O in event loops, and missing cache layers.
   - Verify timeouts, retries, and circuit breakers on external dependencies.
   - **Exit criteria**: I/O bottleneck findings with path and frequency evidence.

5. **Phase 4: Memory & Allocation Review**
   - Inspect large buffer allocations inside tight loops, missing streaming for large payloads, unbounded caches, and memory leaks.
   - **Exit criteria**: Memory findings with allocation sites and growth scenarios.

6. **Phase 5: Concurrency & Contention**
   - Review locks, channels, thread pools, async boundaries, and race-prone state checks.
   - Identify lock contention, worker starvation, and blocking operations on hot paths.
   - **Exit criteria**: Concurrency findings with timing or ordering evidence.

7. **Phase 6: Validation & Prioritization**
   - Reproduce the most impactful findings with safe, isolated measurements or static proof.
   - Rank findings by blast radius, frequency, and fix cost.
   - **Exit criteria**: Validated findings with severity and confidence labels.

8. **Phase 7: Remediation Planning & Artifacts**
   - Design minimal optimizations that preserve correctness.
   - Emit performance audit artifacts.
   - **Exit criteria**: Deliverables written and pre-delivery gates satisfied.

## Required Controls / Checks

- Cite exact file paths and line numbers for every bottleneck claim.
- Report qualitative impact bands (`HIGH`, `MEDIUM`, `LOW`, `UNKNOWN`) instead of fabricated percentages.
- Do not optimize without evidence; avoid speculative rewrites of non-hot paths.
- Ensure reproduction steps are safe and do not overload shared environments.
- Verify that proposed changes do not alter correctness or observable semantics without `[BEHAVIOR CHANGE]` approval.
- Include rollback or revert instructions for high-risk optimizations.

## Artifact Outputs

Use the **Standard** profile for focused performance investigations and the **Exhaustive** profile for release-readiness reviews.

- `HQE_REPORT.md` (performance section and executive summary)
- `HQE_FINDINGS.json`
- `HQE_PATTERN_FINDINGS.md`
- `HQE_RELIABILITY.md`
- `HQE_MASTER_TODO.md`
- `HQE_UNKNOWNS.md`
- `HQE_CONFIDENCE.md`
- `HQE_RUN_MANIFEST.json`
- `HQE_SESSION_LOG.json`
- `HQE_HANDOFF.md` (when remediation is requested)

## Stop-the-Line Conditions

Invoke `workflows/incident-response.md` if the audit discovers:

- A path that causes unbounded resource exhaustion or denial of service under normal input.
- A performance optimization that introduces a critical security flaw or data corruption.
- Active credentials or secrets exposed in performance tooling or benchmarks.

## Confidence Model Reminders

Tag every major claim:

- `[FACT]` — Verified by profile output, load test, or direct code inspection.
- `[INFERENCE]` — Strongly supported by hot-path proximity and complexity analysis.
- `[HYPOTHESIS]` — Plausible bottleneck that requires measurement to confirm.
- `[NEEDS_VERIFICATION]` — Cannot be confirmed with available tools or data.

Never report a performance gain or regression as fact without a reproduced measurement or static proof.
