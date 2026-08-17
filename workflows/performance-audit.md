# Performance Audit Workflow

The `performance` audit workflow (`/HQE performance`) profiles hot paths, identifies bottlenecks, and evaluates concurrency, allocation, and I/O behavior.

## 1. Objective

Find evidence-based performance defects and optimization opportunities. Prioritize issues by real impact on hot paths rather than micro-optimizations. Never invent metrics; report qualitative bands backed by line anchors and, when available, reproducible measurements.

## 2. Prerequisites

Before starting the performance audit, confirm the following:

- [ ] Access to the full repository source, build system, and dependency manifests.
- [ ] Access to existing tests, benchmarks, load tests, or profiling data if available.
- [ ] A safe environment for running profiling or load-generation commands without overloading shared infrastructure.
- [ ] A clean working directory or a defined scope of changed files for PR-based audits.
- [ ] `protocol/hqe-engineer.yaml` and `references/performance-review.md` are available for reference.
- [ ] Schema validators in `scripts/` are runnable (`python3 scripts/validate_findings.py`, etc.).

## 3. Entry Criteria

Begin this workflow when any of the following are true:

- User invokes `/HQE performance`.
- Latency, throughput, or resource-utilization regressions are reported.
- The system is approaching a scale milestone or load target.
- A recent change introduced suspicious complexity, blocking I/O, or memory growth.
- Profiling data, load tests, or production telemetry indicate a bottleneck.

## 4. Stop-the-Line Conditions

Immediately halt the normal audit flow and invoke [`workflows/incident-response.md`](incident-response.md) if the audit discovers:

- A path that causes unbounded resource exhaustion or denial of service under normal input.
- A performance optimization that introduces a critical security flaw or data corruption.
- Active credentials or secrets exposed in performance tooling or benchmarks.

Flag the triggering item as `STOP-THE-LINE: [issue]` in the session log and do not proceed with normal artifact generation until incident response is complete.

## 5. Execution Model

### Phase 0: Orientation & Hot-Path Identification

**Goal**: Establish a repository-grounded understanding of where work actually happens.

1. **Inventory entry points**:
   - HTTP routes/handlers, event handlers, background jobs, CLI commands, message consumers.
   - Record each entry point with `file:line` or `anchor+grep`.
2. **Identify hot-path candidates**:
   - Loops, recursive paths, database queries, cache interactions, external calls, and batch operations.
   - Note paths that run frequently or handle large/unbounded inputs.
3. **Classify input surfaces**:
   - Distinguish bounded from unbounded inputs (payload size, result sets, recursion depth).

**Evidence to collect**:
- Entry-point inventory with frequency or importance notes.
- Ranked list of hot paths and unbounded input surfaces.
- Initial map of data stores and external dependencies touched by hot paths.

**Exit criteria**:
- [ ] A ranked list of hot paths exists.
- [ ] Unbounded input surfaces are identified and anchored to code.

### Phase 1: Baseline & Instrumentation

**Goal**: Capture current behavior before analysis.

1. **Run existing tests**:
   - Execute the test suite and record pass/fail, duration, and any pre-existing failures.
2. **Run profiling or benchmarks when safe**:
   - Use available profilers, load generators, or benchmark commands.
   - Record qualitative observations if quantitative tooling is unavailable.
3. **Document environment**:
   - Note hardware, concurrency level, dataset size, and tooling versions used for measurements.

**Evidence to collect**:
- Baseline metrics or a statement that profiling is unavailable.
- Commands and environment notes for reproducibility.
- Pre-existing failure inventory to avoid misattribution.

**Exit criteria**:
- [ ] Baseline behavior is recorded.
- [ ] If profiling was skipped, the reason is documented.

### Phase 2: Algorithmic Complexity

**Goal**: Find accidental complexity that grows with input size.

1. **Inspect hot paths**:
   - Look for accidental `O(N^2)` or worse complexity on unbounded inputs.
   - Check nested loops, recursive explosion, and combinatorial path growth.
2. **Map input-size bounds**:
   - Determine whether loops are bounded by constants or by user-controlled data.
3. **Check data-structure choices**:
   - Identify linear scans where indexes, sets, or maps would be appropriate.

**Evidence to collect**:
- Complexity findings with input-size bounds.
- Code snippets showing the nested or recursive hotspot.
- `grep` signatures for reproducing the finding.

**Exit criteria**:
- [ ] Complexity findings include input-size bounds and code anchors.
- [ ] Unbounded growth paths are flagged with severity.

### Phase 3: I/O & Network Bottlenecks

**Goal**: Find external and storage bottlenecks on hot paths.

1. **Inspect database access**:
   - Look for N+1 query problems, missing indexes, unbounded result sets, and missing pagination.
2. **Inspect external calls**:
   - Check for unbatched requests, missing timeouts, missing retries, and missing circuit breakers.
3. **Inspect synchronous I/O**:
   - Identify synchronous disk or network operations inside event loops or thread pools.
4. **Review caching**:
   - Check whether cacheable data is recomputed or refetched repeatedly.

**Evidence to collect**:
- I/O bottleneck findings with path and frequency evidence.
- Code snippets showing the query, call, or I/O pattern.
- Evidence of timeout/retry/circuit-breaker presence or absence.

**Exit criteria**:
- [ ] I/O bottleneck findings include path and frequency evidence.
- [ ] Missing timeouts, retries, or circuit breakers are flagged.

### Phase 4: Memory & Allocation Review

**Goal**: Find allocation overhead and memory growth scenarios.

1. **Inspect large allocations**:
   - Look for large buffer allocations inside tight loops or per-request handlers.
2. **Check streaming usage**:
   - Identify places where large payloads are loaded fully into memory instead of streamed.
3. **Find unbounded caches**:
   - Locate caches, queues, or collections that grow without eviction or limits.
4. **Look for memory leaks**:
   - Check for closures holding references, forgotten event listeners, or unreleased connections.

**Evidence to collect**:
- Memory findings with allocation sites and growth scenarios.
- Code snippets showing the allocation or cache pattern.

**Exit criteria**:
- [ ] Memory findings include allocation sites and growth scenarios.
- [ ] Unbounded growth paths are flagged with severity.

### Phase 5: Concurrency & Contention

**Goal**: Find timing, ordering, and resource contention issues.

1. **Review locks and channels**:
   - Identify coarse-grained locks, lock ordering issues, and channel/blocking operations on hot paths.
2. **Inspect thread pools and workers**:
   - Check pool sizes, queue lengths, and starvation scenarios.
3. **Look for race-prone state checks**:
   - Identify time-of-check to time-of-use (TOCTOU) patterns and unprotected shared mutable state.
4. **Check async boundaries**:
   - Verify that blocking calls are not made inside async event loops.

**Evidence to collect**:
- Concurrency findings with timing or ordering evidence.
- Code snippets showing the lock, channel, or race-prone pattern.

**Exit criteria**:
- [ ] Concurrency findings include timing or ordering evidence.
- [ ] Each finding is tagged with confidence and severity.

### Phase 6: Cross-Cutting Impact

**Goal**: Correlate performance findings with security, reliability, and architecture concerns.

1. **Map findings to entry points**:
   - Confirm each bottleneck is reachable from a real entry point, not a hypothetical path.
2. **Assess blast radius**:
   - Estimate how many users, requests, or operations are affected.
3. **Check for trade-offs**:
   - Identify optimizations that would weaken security, correctness, or maintainability.

**Evidence to collect**:
- Cross-cutting impact mapping.
- Blast-radius estimates with entry-point evidence.
- Trade-off notes for risky optimizations.

**Exit criteria**:
- [ ] Each finding is anchored to a real entry point.
- [ ] Security/correctness trade-offs are documented.

### Phase 7: Validation & Prioritization

**Goal**: Confirm impact and rank findings before remediation planning.

1. **Reproduce the most impactful findings**:
   - Use safe, isolated measurements or static proof.
   - Do not overload shared environments.
2. **Rank findings**:
   - Order by blast radius, frequency, and fix cost.
3. **Assign severity and confidence**:
   - Use `[FACT]` only for reproduced measurements or direct code proof.
   - Downgrade to `[HYPOTHESIS]` or `[NEEDS_VERIFICATION]` when measurement is unavailable.

**Evidence to collect**:
- Validated findings with severity and confidence labels.
- Reproduction commands and expected outputs.

**Exit criteria**:
- [ ] Validated findings have severity and confidence labels.
- [ ] No unverified performance claim is reported as fact.

### Phase 8: Remediation Planning & Artifacts

**Goal**: Produce clean, consistent, and internally consistent deliverables.

1. **Deduplicate findings** by root cause.
2. **Design minimal optimizations**:
   - Preserve correctness and observable semantics.
   - Flag any behavior change with `[BEHAVIOR CHANGE]`.
   - Include rollback instructions for high-risk optimizations.
3. **Emit performance audit artifacts**.
4. **Validate** all JSON artifacts against schemas in `schemas/`.

**Evidence to collect**:
- Final artifact set.
- Schema-validation output.
- Confidence declaration and unknowns list.

**Exit criteria**:
- [ ] All deliverables written and pre-delivery gates satisfied.
- [ ] Schema validation passes.

## 6. Required Controls / Checks

- Cite exact file paths and line numbers for every bottleneck claim.
- Report qualitative impact bands (`HIGH`, `MEDIUM`, `LOW`, `UNKNOWN`) instead of fabricated percentages.
- Do not optimize without evidence; avoid speculative rewrites of non-hot paths.
- Ensure reproduction steps are safe and do not overload shared environments.
- Verify that proposed changes do not alter correctness or observable semantics without `[BEHAVIOR CHANGE]` approval.
- Include rollback or revert instructions for high-risk optimizations.
- Use finding IDs `PERF-XXX` for performance issues and `REL-XXX` for reliability-affecting issues.

## 7. Artifact Outputs

Use the **Standard** profile for focused performance investigations and the **Exhaustive** profile for release-readiness reviews.

- `HQE_REPORT.md` (performance section and executive summary)
- `HQE_FINDINGS.json` (machine-readable performance findings)
- `HQE_PATTERN_FINDINGS.md`
- `HQE_RELIABILITY.md`
- `HQE_MASTER_TODO.md`
- `HQE_UNKNOWNS.md`
- `HQE_CONFIDENCE.md`
- `HQE_RUN_MANIFEST.json`
- `HQE_SESSION_LOG.json`
- `HQE_HANDOFF.md` (when remediation is requested)

Validate machine-readable artifacts with:

```bash
python3 scripts/validate_findings.py HQE_FINDINGS.json
python3 scripts/validate_manifest.py HQE_RUN_MANIFEST.json
python3 scripts/validate_session_log.py HQE_SESSION_LOG.json
```

## 8. Exit Criteria

The performance audit is complete when:

- [ ] All phases above have been executed or explicitly skipped with justification.
- [ ] Every performance finding cites concrete code evidence.
- [ ] Reproduced measurements or static proof back every major claim.
- [ ] Behavior-changing recommendations are flagged with `[BEHAVIOR CHANGE]`.
- [ ] Artifacts are emitted and schema-validated.
- [ ] Stop-the-line conditions have been checked; if triggered, incident response has been invoked.
- [ ] The session log is updated with completed, in-progress, discovered, and reprioritized items.

## 9. Confidence Model Reminders

Tag every major claim:

- `[FACT]` — Verified by profile output, load test, or direct code inspection.
- `[INFERENCE]` — Strongly supported by hot-path proximity and complexity analysis.
- `[HYPOTHESIS]` — Plausible bottleneck that requires measurement to confirm.
- `[NEEDS_VERIFICATION]` — Cannot be confirmed with available tools or data.

Never report a performance gain or regression as fact without a reproduced measurement or static proof.
