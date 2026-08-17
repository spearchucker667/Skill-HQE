# Reliability Review Guide

When performing a reliability audit (`/HQE reliability`), focus on fault tolerance, error recovery, and system invariants.

## 1. Core Reliability Dimensions
1. **Unhandled Failure Modes**: Missing error handling on remote RPCs, database disconnections, or filesystem failures.
2. **Concurrency Invariants & Race Conditions**: Check-then-act race conditions (TOCTOU), unsynchronized shared memory, or deadlock scenarios.
3. **Resource Leakage**: Unclosed sockets, lingering database connections, or uncleaned temporary files.
4. **Graceful Degradation**: Fallback mechanisms when upstream services or dependencies fail.
5. **Backpressure & Rate Limiting**: Handling burst traffic without exhausting memory or thread pools.
