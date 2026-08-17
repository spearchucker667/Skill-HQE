# Rust Diagnostic Guide

## 1. Project Orientation & Manifests
- **Manifests**: `Cargo.toml`, `Cargo.lock`, workspace configurations (`[workspace]`).
- **Tooling**: `cargo`, `rustup`, `clippy`, `rustfmt`.

## 2. Common Defect Patterns
1. **Unsound `unsafe` Blocks**: Unvalidated pointer arithmetic, aliasing violations, or breaking Rust's strict safety invariants.
2. **Panic in Production Paths**: Overuse of `.unwrap()` or `.expect()` in network/parsing handlers that crash the thread or service.
3. **Deadlocks & Lock Contention**: Inconsistent lock acquisition order across `std::sync::Mutex` / `parking_lot::RwLock`, or holding sync locks across `.await` points.
4. **Clone Bloat / Excessive Allocations**: Unnecessary `.clone()` calls inside tight loops instead of using borrowing or `Arc`/`Rc` references.
5. **Channel Deadlocks**: Unbounded or mismanaged `tokio::sync::mpsc` channels causing memory leaks or worker thread hangs.

## 3. Verification & Validation Commands
```bash
# Check Compilation
cargo check --all-targets

# Lints & Warnings
cargo clippy --all-targets -- -D warnings

# Tests
cargo test --all
```
