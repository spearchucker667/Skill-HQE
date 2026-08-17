# Go Diagnostic Guide

## 1. Project Orientation & Manifests
- **Manifests**: `go.mod`, `go.sum`, `vendor/` directory.
- **Tooling**: `go`, `golangci-lint`, `govulncheck`.

## 2. Common Defect Patterns
1. **Goroutine Leaks**: Spawning goroutines without context cancellation (`ctx.Done()`) or blocking on unbuffered channels with no reader.
2. **Data Races**: Concurrent access to shared maps or slices without `sync.Mutex` or `sync.RWMutex`.
3. **Nil Pointer Dereferences**: Accessing struct fields or map keys after an unchecked failed error return (`if err != nil`).
4. **Shadowed Variables**: Inadvertent `:=` inside an `if` block shadowing an outer error variable.
5. **Defer in Loops**: Deferring resource closes (`defer resp.Body.Close()`) inside long-running loops causing resource starvation until loop exit.

## 3. Verification & Validation Commands
```bash
# Linting
golangci-lint run

# Race Detector & Tests
go test -v -race ./...

# Vulnerability Audit
govulncheck ./...
```
