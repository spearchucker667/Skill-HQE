#!/usr/bin/env python3
import sys
import json
import argparse
from pathlib import Path

try:
    from jsonschema import validate, ValidationError
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False

def main():
    parser = argparse.ArgumentParser(description="Validate HQE run manifest JSON against schema.")
    parser.add_argument("manifest_file", help="Path to run manifest JSON file")
    args = parser.parse_args()

    manifest_path = Path(args.manifest_file)
    schema_path = Path(__file__).parent.parent / "schemas" / "run-manifest.schema.json"

    if not manifest_path.exists():
        print(f"Error: {manifest_path} does not exist", file=sys.stderr)
        sys.exit(1)

    try:
        with open(manifest_path) as f:
            manifest = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}", file=sys.stderr)
        sys.exit(1)

    if not HAS_JSONSCHEMA:
        print("Error: jsonschema module is required for validation.", file=sys.stderr)
        sys.exit(1)

    try:
        with open(schema_path) as f:
            schema = json.load(f)
        
        validate(instance=manifest, schema=schema)
        print("Validation successful!")
    except ValidationError as e:
        print(f"Validation error: {e.message}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error during validation: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
