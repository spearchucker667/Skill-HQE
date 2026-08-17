#!/usr/bin/env python3
"""
HQE Engineer Protocol YAML Validator (Python)

Validates hqe-engineer.yaml against hqe-schema.json
Usage: python3 verify.py [--yaml path/to/file.yaml] [--schema path/to/schema.json]

Exit codes:
    0 - Validation successful
    1 - Validation failed
    2 - File not found or other error
"""

import argparse
import json
import sys
from pathlib import Path

try:
    import yaml
    from jsonschema import validate, ValidationError, Draft202012Validator
except ImportError as e:
    print(f"Error: Missing required dependency - {e}")
    print("Install with: pip install pyyaml jsonschema")
    sys.exit(2)


def load_yaml(filepath: Path) -> dict:
    """Load and parse YAML file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def load_json(filepath: Path) -> dict:
    """Load and parse JSON file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def validate_yaml(yaml_data: dict, schema: dict) -> tuple[bool, list]:
    """
    Validate YAML data against schema.
    Returns (is_valid, errors).
    """
    errors = []
    
    try:
        validate(instance=yaml_data, schema=schema)
        return True, []
    except ValidationError as e:
        errors.append({
            'message': e.message,
            'path': list(e.path) if e.path else ['root'],
            'schema_path': list(e.schema_path) if e.schema_path else [],
            'validator': e.validator,
            'validator_value': e.validator_value
        })
        return False, errors


def print_validation_errors(errors: list):
    """Pretty print validation errors."""
    print("\n❌ Validation Errors:")
    print("=" * 60)
    
    for i, error in enumerate(errors, 1):
        print(f"\nError #{i}:")
        print(f"  Message: {error['message']}")
        print(f"  Path: {' -> '.join(str(p) for p in error['path'])}")
        if error['schema_path']:
            print(f"  Schema Path: {' -> '.join(str(p) for p in error['schema_path'])}")
        if error['validator']:
            print(f"  Validator: {error['validator']}")


def print_summary(yaml_data: dict, schema: dict, is_valid: bool):
    """Print validation summary."""
    print("\n" + "=" * 60)
    if is_valid:
        print("✅ VALIDATION PASSED")
    else:
        print("❌ VALIDATION FAILED")
    print("=" * 60)
    
    # Print metadata
    print("\n📋 Protocol Metadata:")
    print(f"  Schema Version:    {yaml_data.get('schema_version', 'N/A')}")
    print(f"  Protocol Version:  {yaml_data.get('protocol_version', 'N/A')}")
    print(f"  Last Updated:      {yaml_data.get('last_updated', 'N/A')}")
    print(f"  License:           {yaml_data.get('license', 'N/A')}")
    print(f"  Maintainer:        {yaml_data.get('maintainer', 'N/A')}")
    
    role = yaml_data.get('role', {})
    print(f"  Role:              {role.get('title', 'N/A')}")
    
    # Print structure info
    print("\n📊 Structure Summary:")
    phases = yaml_data.get('phases', {})
    print(f"  Phases defined:    {len(phases)}")
    for phase_name in phases.keys():
        print(f"    - {phase_name}")
    
    constraints = yaml_data.get('hard_constraints', [])
    print(f"  Hard constraints:  {len(constraints)}")
    
    principles = yaml_data.get('operating_principles', [])
    print(f"  Operating principles: {len(principles)}")
    
    anti_patterns = yaml_data.get('anti_patterns', [])
    print(f"  Anti-patterns:     {len(anti_patterns)}")


def main():
    parser = argparse.ArgumentParser(
        description='Validate HQE Engineer YAML against JSON Schema',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 verify.py
  python3 verify.py --yaml custom.yaml --schema custom-schema.json
  python3 verify.py --verbose
        """
    )
    
    parser.add_argument(
        '--yaml', '-y',
        type=Path,
        default=Path('hqe-engineer.yaml'),
        help='Path to YAML file (default: hqe-engineer.yaml)'
    )
    
    parser.add_argument(
        '--schema', '-s',
        type=Path,
        default=Path('hqe-schema.json'),
        help='Path to JSON schema file (default: hqe-schema.json)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    args = parser.parse_args()
    
    # Check files exist
    if not args.yaml.exists():
        print(f"Error: YAML file not found: {args.yaml}")
        sys.exit(2)
    
    if not args.schema.exists():
        print(f"Error: Schema file not found: {args.schema}")
        sys.exit(2)
    
    try:
        # Load files
        if args.verbose:
            print(f"Loading YAML: {args.yaml}")
        yaml_data = load_yaml(args.yaml)
        
        if args.verbose:
            print(f"Loading Schema: {args.schema}")
        schema = load_json(args.schema)
        
        # Validate
        if args.verbose:
            print("Validating...")
        
        is_valid, errors = validate_yaml(yaml_data, schema)
        
        if not is_valid:
            print_validation_errors(errors)
        
        print_summary(yaml_data, schema, is_valid)
        
        sys.exit(0 if is_valid else 1)
        
    except yaml.YAMLError as e:
        print(f"Error: Invalid YAML syntax - {e}")
        sys.exit(2)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON syntax in schema - {e}")
        sys.exit(2)
    except Exception as e:
        print(f"Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(2)


if __name__ == '__main__':
    main()
