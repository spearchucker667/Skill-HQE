#!/usr/bin/env python3
import sys
import json
import jsonschema

def main():
    if len(sys.argv) != 2:
        print("Usage: validate_session_log.py <path_to_log.json>")
        sys.exit(1)

    log_path = sys.argv[1]
    schema_path = "schemas/session-log.schema.json"

    with open(schema_path) as f:
        schema = json.load(f)

    with open(log_path) as f:
        log_data = json.load(f)

    try:
        jsonschema.validate(instance=log_data, schema=schema)
        print(f"Validation successful: {log_path}")
    except jsonschema.exceptions.ValidationError as e:
        print(f"Validation failed: {e.message}")
        sys.exit(1)

if __name__ == "__main__":
    main()
