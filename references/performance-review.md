# Performance Review Guide

When performing a performance audit (`/HQE performance`), prioritize hot-path execution, allocation overhead, and I/O bottlenecks.

## 1. Core Performance Dimensions
1. **Algorithmic Complexity**: Unnecessary $O(N^2)$ or $O(2^N)$ algorithms in request handling paths or dataset processing.
2. **I/O & Network Bottlenecks**: Unbatched queries (N+1 query problems), synchronous disk operations in event loops, or missing cache layers.
3. **Memory Bloat & Allocations**: Large buffer allocations inside tight loops, missing streaming for large file payloads, or unchecked caching arrays.
4. **Concurrency & Contention**: Lock contention in high-throughput data paths, worker thread starvation, or blocking channel operations.
