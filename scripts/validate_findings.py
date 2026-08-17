#!/usr/bin/env python3
import sys
import json
import argparse
from pathlib import Path

# Fallback basic schema validation if jsonschema is not installed
try:
    from jsonschema import validate, ValidationError
    from referencing import Registry, Resource
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False

def main():
    parser = argparse.ArgumentParser(description="Validate HQE findings JSON against schema.")
    parser.add_argument("findings_file", help="Path to findings JSON file")
    args = parser.parse_args()

    findings_path = Path(args.findings_file)
    schema_path = Path(__file__).parent.parent / "schemas" / "findings.schema.json"
    finding_schema_path = Path(__file__).parent.parent / "schemas" / "finding.schema.json"

    if not findings_path.exists():
        print(f"Error: {findings_path} does not exist", file=sys.stderr)
        sys.exit(1)

    try:
        with open(findings_path) as f:
            findings = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}", file=sys.stderr)
        sys.exit(1)

    if not HAS_JSONSCHEMA:
        print("Error: jsonschema module is required for validation.", file=sys.stderr)
        sys.exit(1)

    # Full validation
    try:
        with open(schema_path) as f:
            schema = json.load(f)
        with open(finding_schema_path) as f:
            finding_schema = json.load(f)
            
        registry = Registry().with_resource(
            "finding.schema.json", Resource.from_contents(finding_schema)
        )
        validate(instance=findings, schema=schema, registry=registry)
        print("Validation successful!")
    except ValidationError as e:
        print(f"Validation error: {e.message}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error during validation: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
