# HQE Engineer Protocol

This folder contains the HQE Engineer protocol definition and its validation schema.

## Files

- `hqe-engineer.yaml` - Protocol source of truth (YAML)
- `hqe-schema.json` - JSON schema used by validators and tooling
- `verify.py` / `validate.py` - Python validation scripts
- `VALIDATORS.md` - Notes on validation and versioning
- `archive/` - Prior protocol versions and historical docs

## Validate Locally

From repo root:

```bash
./scripts/validate_protocol.sh
```

Or via the CLI:

```bash
cargo build --release -p hqe
./target/release/hqe validate-protocol
```

Notes:
- If Python is installed without `pyyaml`/`jsonschema`, the CLI will fall back to basic syntax validation.
- CI installs Python dependencies so full schema validation runs there.

