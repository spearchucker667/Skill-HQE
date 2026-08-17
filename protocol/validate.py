#!/usr/bin/env python3
"""
HQE Engineer Protocol Validator

Validates HQE Engineer YAML protocol files against the JSON Schema.
Also performs additional semantic linting.

Usage:
    python validate.py <path_to_yaml_file>
    python validate.py --schema  # Validate the schema itself
"""

import sys
import json
import yaml
from pathlib import Path
from typing import List, Dict, Any, Tuple

# Try to import jsonschema, fall back to basic validation if not available
try:
    from jsonschema import validate, ValidationError, Draft7Validator
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False
    print("Warning: jsonschema not installed. Install with: pip install jsonschema")


def load_yaml(path: Path) -> Dict[str, Any]:
    """Load YAML file."""
    with open(path, 'r') as f:
        return yaml.safe_load(f)


def load_json(path: Path) -> Dict[str, Any]:
    """Load JSON file."""
    with open(path, 'r') as f:
        return json.load(f)


def validate_schema_structure(schema: Dict[str, Any]) -> List[str]:
    """Perform basic validation of the schema itself."""
    errors = []
    
    # Check required top-level fields
    required_fields = ['$schema', 'type', 'properties']
    for field in required_fields:
        if field not in schema:
            errors.append(f"Schema missing required field: {field}")
    
    # Check for id_prefixes pattern
    if 'properties' in schema:
        defs = schema['properties'].get('definitions', {})
        if 'properties' in defs:
            id_prefixes = defs['properties'].get('id_prefixes', {})
            if 'patternProperties' in id_prefixes:
                pattern = list(id_prefixes['patternProperties'].keys())[0]
                if pattern != "^[A-Z]{3,6}$":
                    errors.append(f"id_prefixes pattern may be incorrect: {pattern}")
    
    return errors


def validate_yaml_semantics(data: Dict[str, Any]) -> List[str]:
    """Perform semantic validation beyond schema."""
    errors = []
    warnings = []
    
    # Check version consistency
    schema_version = data.get('schema_version', '')
    protocol_version = data.get('protocol_version', '')
    
    if schema_version != protocol_version:
        warnings.append(f"schema_version ({schema_version}) != protocol_version ({protocol_version})")
    
    # Check for required ID prefixes
    definitions = data.get('definitions', {})
    id_prefixes = definitions.get('id_prefixes', {})
    
    required_prefixes = ['BOOT', 'SEC', 'BUG', 'PERF', 'DOC']
    for prefix in required_prefixes:
        if prefix not in id_prefixes:
            errors.append(f"Missing required ID prefix: {prefix}")
    
    # Check constraints have proper IDs
    constraints = data.get('constraints', [])
    expected_id = 1
    for constraint in constraints:
        cid = constraint.get('id', '')
        expected_cid = f"C{expected_id}"
        if cid != expected_cid:
            errors.append(f"Constraint ID out of order: expected {expected_cid}, got {cid}")
        expected_id += 1
    
    # Check phases exist
    phases = data.get('phases', {})
    required_phases = ['phase_zero', 'phase_one', 'phase_two', 'phase_three']
    for phase in required_phases:
        if phase not in phases:
            errors.append(f"Missing required phase: {phase}")
    
    # Check output controls
    output_controls = data.get('output_controls', {})
    size_limits = output_controls.get('size_limits', {})
    
    critical_max = size_limits.get('critical_and_high_max_total', 0)
    if critical_max < 20 or critical_max > 50:
        warnings.append(f"critical_and_high_max_total ({critical_max}) seems unusual")
    
    # Check anti-patterns
    anti_patterns = data.get('anti_patterns', {})
    prohibited = anti_patterns.get('prohibited', [])
    if len(prohibited) < 5:
        warnings.append(f"Only {len(prohibited)} anti-patterns defined (recommend >10)")
    
    # Check pre-delivery checklist
    pre_delivery = data.get('pre_delivery_checklist', {})
    mandatory = pre_delivery.get('mandatory_checks', [])
    if len(mandatory) < 5:
        warnings.append(f"Only {len(mandatory)} mandatory checks (recommend >10)")
    
    return errors, warnings


def validate_with_schema(data: Dict[str, Any], schema: Dict[str, Any]) -> List[str]:
    """Validate data against JSON schema."""
    errors = []
    
    if not HAS_JSONSCHEMA:
        return ["jsonschema not installed, skipping schema validation"]
    
    try:
        validate(instance=data, schema=schema)
    except ValidationError as e:
        errors.append(f"Schema validation error: {e.message}")
        errors.append(f"  Path: {'/'.join(str(p) for p in e.path)}")
    
    return errors


def lint_yaml_file(yaml_path: Path, schema_path: Path = None) -> Tuple[bool, List[str], List[str]]:
    """
    Lint a YAML file against schema and semantics.
    
    Returns: (is_valid, errors, warnings)
    """
    errors = []
    warnings = []
    
    # Load YAML
    try:
        data = load_yaml(yaml_path)
    except yaml.YAMLError as e:
        return False, [f"YAML parse error: {e}"], []
    
    # Load schema if provided
    if schema_path and schema_path.exists():
        try:
            schema = load_json(schema_path)
            # Validate schema itself
            schema_errors = validate_schema_structure(schema)
            if schema_errors:
                warnings.extend([f"Schema issue: {e}" for e in schema_errors])
            
            # Validate against schema
            schema_errors = validate_with_schema(data, schema)
            errors.extend(schema_errors)
        except Exception as e:
            warnings.append(f"Could not validate against schema: {e}")
    
    # Semantic validation
    sem_errors, sem_warnings = validate_yaml_semantics(data)
    errors.extend(sem_errors)
    warnings.extend(sem_warnings)
    
    return len(errors) == 0, errors, warnings


def main():
    if len(sys.argv) < 2:
        print("Usage: python validate.py <path_to_yaml_file>")
        print("       python validate.py --schema  # Validate schema")
        sys.exit(1)
    
    arg = sys.argv[1]
    
    # Get paths
    script_dir = Path(__file__).parent
    schema_path = script_dir / "hqe-engineer-schema.json"
    
    if arg == "--schema":
        # Validate the schema itself
        if schema_path.exists():
            try:
                schema = load_json(schema_path)
                errors = validate_schema_structure(schema)
                if errors:
                    print("Schema validation errors:")
                    for e in errors:
                        print(f"  - {e}")
                    sys.exit(1)
                else:
                    print("✓ Schema is valid")
                    sys.exit(0)
            except Exception as e:
                print(f"Error loading schema: {e}")
                sys.exit(1)
        else:
            print(f"Schema not found: {schema_path}")
            sys.exit(1)
    
    # Validate YAML file
    yaml_path = Path(arg)
    if not yaml_path.exists():
        print(f"File not found: {yaml_path}")
        sys.exit(1)
    
    print(f"Validating: {yaml_path}")
    if schema_path.exists():
        print(f"Using schema: {schema_path}")
    print()
    
    is_valid, errors, warnings = lint_yaml_file(yaml_path, schema_path)
    
    if warnings:
        print("Warnings:")
        for w in warnings:
            print(f"  ⚠ {w}")
        print()
    
    if errors:
        print("Errors:")
        for e in errors:
            print(f"  ✗ {e}")
        print()
        print(f"Validation FAILED: {len(errors)} error(s)")
        sys.exit(1)
    else:
        print(f"✓ Validation passed")
        if warnings:
            print(f"  ({len(warnings)} warning(s) - review recommended)")
        sys.exit(0)


if __name__ == "__main__":
    main()
