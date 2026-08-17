# Large Repository Strategy

When auditing large repositories (>50 files), you cannot pretend that a small sample equates to an exhaustive review. You must adopt a rigorous coverage model.

## Triage and Coverage Steps

1. **Inventory**: Build a complete file inventory. Use the `scripts/inventory_repo.py` helper if available.
2. **Classify**: Group files by subsystem and relative risk.
3. **Exclude Noise**: Exclude generated, vendored, or build output directories from substantive coverage unless explicitly relevant.
4. **Prioritize Entrypoints**: Inspect manifests (`package.json`, `Cargo.toml`, etc.) and application entrypoints first.
5. **Prioritize Risk**: Focus early attention on:
   - Changed code (if reviewing a PR)
   - Trust boundaries and network interfaces
   - Authentication and authorization logic
   - Serialization/deserialization
   - Concurrency and state management
6. **Parallelize (if supported)**: If your environment supports spawning subagents, distribute the review by subsystem.
7. **Maintain a Ledger**: Track what you have reviewed and the depth of review.
8. **Explicit Limitations**: In your final report, explicitly state what surfaces were **NOT** reviewed.

## The Coverage Ledger
Maintain a ledger in your notes or final report resembling:

| Subsystem | Files | Reviewed | Depth | Findings | Notes |
|-----------|-------|----------|-------|----------|-------|
| `api/`    | 45    | Yes      | Deep  | 3        | Focused on auth middleware |
| `ui/`     | 120   | Partial  | Scan  | 1        | Checked for obvious XSS    |
| `legacy/` | 300   | No       | None  | 0        | Excluded from scope        |

**Do not claim a "line-by-line exhaustive review" unless the actual process executed supports that claim.**
