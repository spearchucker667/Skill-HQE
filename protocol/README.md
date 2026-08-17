# HQE Engineer Protocol

This folder contains the canonical HQE Engineer protocol definition and its validation schema.

## Files

- `hqe-engineer.yaml` - Active protocol source of truth (YAML)
- `hqe-engineer-schema.json` - JSON Schema Draft 2020-12 specification for the protocol YAML; validates `hqe-engineer.yaml`
- `hqe-schema.json` - Legacy/tooling schema used by `verify.py`; kept for backwards compatibility with v3.x-v4.x verification workflows
- `validate.py` - Canonical protocol validator with semantic linting
- `verify.py` - Standalone verbose verifier with structured error output
- `VALIDATORS.md` - Notes on validation and versioning
- `HQE_v5_MIGRATION_NOTES.md` - v5.0.0 migration notes
- `SOURCE_CHECKSUMS.sha256` - SHA-256 checksums of canonical protocol files

## Validate Locally

From the repository root:

```bash
# Validate the protocol YAML against its schema
python3 protocol/validate.py protocol/hqe-engineer.yaml

# Validate the schema itself
python3 protocol/validate.py --schema

# Validate the full protocol bundle
python3 scripts/validate_protocol_bundle.py

# Verify canonical checksums
python3 scripts/check_protocol_sync.py
```

Notes:
- Python 3.10+ is required.
- Install dev dependencies with `pip install -e ".[dev]"` or `pip install -r requirements-dev.txt`.
- CI runs the same validators on every push and pull request.

## HQE Protocol v5.0.0 Updates

- Unified YAML/schema version alignment.
- Added control-plane enforcement requirements.
- Added finding lifecycle states and artifact taxonomy.
- Strengthened reproducibility, regression, and delivery gates.
