# HQE Engineering Quality Gates

This reference translates the high-value evaluation gates from HQE Workbench into executable criteria for codebase audits and remediation sign-offs.

---

## 1. Code Quality Gate (`code-quality`)
- [ ] **Idiomatic Patterns**: Follows language idioms and best practices (e.g. RAII/ownership in Rust, typing in TypeScript/Python, proper error handling in Go).
- [ ] **Cyclomatic Complexity**: Functions avoid excessive nesting (max 4 levels) and high branching complexity.
- [ ] **Dead Code Elimination**: No uncalled functions, unused variables, or obsolete commented-out code.
- [ ] **Explicit Resource Cleanup**: All sockets, file descriptors, DB connections, and locks are cleanly released in error paths.

---

## 2. Framework & Runtime Compliance Gate (`framework-compliance`)
- [ ] **Supported Runtime Versions**: Dependencies and syntax conform to the declared engines/runtime (e.g. Node 20+, Python 3.10+, Rust 2021 edition).
- [ ] **Lifecycle Adherence**: Correct use of framework lifecycles (React hooks rules, Tokio async boundaries, FastAPI dependency injection).
- [ ] **Configuration Isolation**: Secrets and environment-dependent variables are loaded via config providers, never hardcoded.

---

## 3. Plan & Remediation Quality Gate (`plan-quality`)
- [ ] **Root-Cause Focus**: The plan solves the foundational defect rather than patching symptoms.
- [ ] **Change Budget**: The proposed modification modifies $\le 5$ files unless an architectural rationale is approved.
- [ ] **Behavior Invariants**: Explicitly identifies if user-visible behavior changes (`[BEHAVIOR CHANGE]`).
- [ ] **Rollback Strategy**: Includes step-by-step instructions to revert changes if regressions occur.

---

## 4. PR Performance Gate (`pr-performance`)
- [ ] **Algorithmic Complexity**: No inadvertent $O(N^2)$ or $O(2^N)$ algorithms introduced on unbounded user inputs.
- [ ] **Database & Network Efficiencies**: Avoids N+1 query patterns; ensures pagination on list endpoints; enforces request timeouts.
- [ ] **Memory Allocation**: Buffers and streams are utilized for large payload processing; avoids loading entire files into RAM.

---

## 5. PR Security Gate (`pr-security`)
- [ ] **Input Validation & Sanitization**: All untrusted inputs are validated at system boundaries before processing.
- [ ] **Taint Chain Integrity**: Untrusted data cannot reach injection sinks (SQL, OS command, Eval, HTML/DOM, SSRF).
- [ ] **Authentication & Authorization**: Endpoints verify session/token validity and enforce tenant/role boundaries.
- [ ] **Secret Hygiene**: Zero raw keys, tokens, or credentials in code or diffs.

---

## 6. Technical Accuracy Gate (`technical-accuracy`)
- [ ] **Evidence Citing**: All claims quote exact line numbers and code snippets from the target repository.
- [ ] **Syntactic Correctness**: Modified code passes syntax checks, typechecking, and compilation.
- [ ] **Semantic Coherence**: No broken assumptions regarding API contracts, return types, or parameter ordering.

---

## 7. Test Coverage & Fixture Realism Gate (`test-coverage`)
- [ ] **Regression Tests**: Every bug fix includes a dedicated regression test that fails before the fix and passes after.
- [ ] **Negative Testing**: Tests cover error conditions, invalid inputs, edge cases, and boundary values.
- [ ] **Deterministic Execution**: Tests do not rely on nondeterministic sleeps, uncontrolled network requests, or race conditions.
