# HQE Engineer Protocol Validators

This directory contains validation scripts to verify that `hqe-engineer.yaml` conforms to the protocol schema.

## Available Validators

| Validator | Schema | Purpose |
|-----------|--------|---------|
| `verify.py` | `hqe-schema.json` | Original v3.x validator |
| `validate.py` | `hqe-engineer-schema.json` | Enhanced v4.0+ validator with semantic linting |

## Quick Start

```bash
# Validate protocol (v4.0+ enhanced validator)
python3 protocol/validate.py protocol/hqe-engineer.yaml

# Validate the schema itself
python3 protocol/validate.py --schema

# Original v3.x validator
python3 protocol/verify.py --verbose

# Or use the project script
./scripts/validate_protocol.sh
```

---

## Enhanced Validator (v4.0+)

**File:** `validate.py`  
**Schema:** `hqe-engineer-schema.json`

### Requirements

- Python 3.8+
- PyYAML (`pip install pyyaml`)
- jsonschema (`pip install jsonschema`) - optional but recommended

### Installation

```bash
pip install pyyaml jsonschema
```

### Usage

```bash
# Validate protocol YAML
python3 validate.py hqe-engineer.yaml

# Validate with specific schema
python3 validate.py --schema-file custom-schema.json hqe-engineer.yaml

# Validate the schema itself
python3 validate.py --schema

# Help
python3 validate.py --help
```

### Features

- Full JSON Schema Draft 7 validation
- Semantic validation beyond schema:
  - ID prefix completeness
  - Constraint ID ordering
  - Phase completeness
  - Output control reasonableness
  - Anti-pattern coverage
- Detailed error messages with path information
- Warning system for non-critical issues
- Exit codes for CI/CD integration

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Validation successful (warnings may exist) |
| 1 | Validation failed (schema mismatch or semantic errors) |
| 2 | File not found or other error |

---

## Original Validator (v3.x)

**File:** `verify.py`  
**Schema:** `hqe-schema.json`

### Usage

```bash
# Basic validation
python3 verify.py

# Verbose output
python3 verify.py --verbose

# Custom files
python3 verify.py --yaml custom.yaml --schema custom-schema.json
```

### Features

- Full JSON Schema Draft 2020-12 validation
- Detailed error messages with path information
- Pretty-printed validation summary
- Metadata extraction and display
- Version compatibility checking

---

## CI/CD Integration

### GitHub Actions

```yaml
name: Validate HQE Protocol

on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install pyyaml jsonschema
      
      - name: Validate YAML (v4.0+)
        run: python3 protocol/validate.py protocol/hqe-engineer.yaml
      
      - name: Validate Schema
        run: python3 protocol/validate.py --schema
```

### Pre-commit Hook

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: validate-hqe
        name: Validate HQE Protocol
        entry: python3 protocol/validate.py
        language: system
        files: hqe-engineer\.yaml$
        pass_filenames: true
```

---

## Schema Validation Details

### What Gets Validated (v4.0+)

1. **File Structure**
   - Valid YAML/JSON syntax
   - Root object type
   - Required fields presence

2. **Metadata**
   - Schema version format (semver)
   - Protocol version format (semver)
   - Date format (ISO 8601)

3. **Content Structure**
   - Role definition with title and mandate
   - Operating principles
   - Scope definition
   - Constraints with proper IDs
   - All phases defined (0 through 4)
   - Output structure
   - Artifact specifications

4. **Semantic Validation**
   - Required ID prefixes present (BOOT, SEC, BUG, etc.)
   - Constraint IDs in sequence (C1, C2, ...)
   - Phase IDs valid
   - Output limits reasonable
   - Anti-patterns defined
   - Pre-delivery checklist present

5. **Type Safety**
   - String fields contain strings
   - Arrays contain expected elements
   - Objects have required properties
   - Numeric fields accept integers and decimals

---

## Troubleshooting

### "No module named 'yaml'"

```bash
pip install pyyaml jsonschema
```

### "No module named 'jsonschema'"

```bash
pip install jsonschema
```

### Schema Version Mismatch

If you see warnings about version mismatches between `schema_version` and `protocol_version`, this is informational. They should typically match but may differ during development.

---

## Extending Validation

To add custom validation rules, edit the `validate_yaml_semantics()` function in `validate.py`.

---

## Version History

- **v4.0.0** (2026-01-28): Added enhanced validator with semantic linting
- **v3.1.0** (2026-01-27): Original validator with JSON Schema support

---

## License

MIT - Same as HQE Engineer Protocol
