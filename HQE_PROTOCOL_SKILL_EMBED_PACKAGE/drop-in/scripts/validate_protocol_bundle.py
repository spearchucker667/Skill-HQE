#!/usr/bin/env python3
"""Validate the embedded HQE protocol bundle.

This wrapper validates the canonical protocol and catches integration drift that
the source validator may not report, while leaving protocol files unchanged.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

try:
    import yaml
    from jsonschema import Draft7Validator, FormatChecker
except ImportError as exc:
    print(
        "ERROR: Full HQE protocol validation requires PyYAML and jsonschema.\n"
        "Install development dependencies before validating.\n"
        f"Missing dependency: {exc}",
        file=sys.stderr,
    )
    raise SystemExit(2)


SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")


def load_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    if not isinstance(data, dict):
        raise ValueError("Protocol root must be a YAML mapping/object.")
    return data


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise ValueError("Schema root must be a JSON object.")
    return data


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Skill-HQE repository root.",
    )
    parser.add_argument(
        "--strict-schema-metadata",
        action="store_true",
        help="Fail if schema title/$id do not mention the active protocol version.",
    )
    args = parser.parse_args()

    root = args.root.resolve()
    protocol_path = root / "protocol" / "hqe-engineer.yaml"
    schema_path = root / "protocol" / "hqe-engineer-schema.json"

    for path in (protocol_path, schema_path):
        if not path.is_file():
            print(f"ERROR: missing required protocol file: {path}", file=sys.stderr)
            return 2

    try:
        protocol = load_yaml(protocol_path)
        schema = load_json(schema_path)
    except Exception as exc:
        print(f"ERROR: parse failure: {exc}", file=sys.stderr)
        return 2

    errors: list[str] = []
    warnings: list[str] = []

    try:
        Draft7Validator.check_schema(schema)
    except Exception as exc:
        errors.append(f"JSON Schema is invalid: {exc}")
    else:
        validator = Draft7Validator(schema, format_checker=FormatChecker())
        for err in sorted(validator.iter_errors(protocol), key=lambda e: list(e.path)):
            loc = ".".join(str(part) for part in err.path) or "<root>"
            errors.append(f"schema:{loc}: {err.message}")

    schema_version = str(protocol.get("schema_version", ""))
    protocol_version = str(protocol.get("protocol_version", ""))

    if not SEMVER_RE.fullmatch(schema_version):
        errors.append(f"schema_version is not semver: {schema_version!r}")
    if not SEMVER_RE.fullmatch(protocol_version):
        errors.append(f"protocol_version is not semver: {protocol_version!r}")
    if schema_version != protocol_version:
        errors.append(
            f"schema_version ({schema_version}) != protocol_version ({protocol_version})"
        )

    # Key protocol invariants expected by /HQE.
    required_top_level = [
        "meta",
        "definitions",
        "role",
        "operating_principles",
        "hard_constraints",
        "phases",
        "constraints",
        "output_controls",
        "pre_delivery_checklist",
    ]
    for key in required_top_level:
        if key not in protocol:
            errors.append(f"missing required HQE control section: {key}")

    prefixes = (
        protocol.get("definitions", {}).get("id_prefixes", {})
        if isinstance(protocol.get("definitions"), dict)
        else {}
    )
    for prefix in ("BOOT", "SEC", "BUG", "REL", "PERF", "UX", "DX", "DOC", "DEBT", "DEPS"):
        if prefix not in prefixes:
            errors.append(f"missing canonical finding prefix: {prefix}")

    phases = protocol.get("phases", {})
    if isinstance(phases, dict):
        for phase in (
            "phase_minus_one",
            "phase_zero",
            "phase_zero_five",
            "phase_one",
            "phase_two",
            "phase_three",
            "phase_four",
        ):
            if phase not in phases:
                errors.append(f"missing canonical phase: {phase}")
    else:
        errors.append("phases must be an object")

    schema_id = str(schema.get("$id", ""))
    schema_title = str(schema.get("title", ""))
    if protocol_version and protocol_version not in schema_id:
        msg = f"schema $id does not contain protocol version {protocol_version}: {schema_id}"
        (errors if args.strict_schema_metadata else warnings).append(msg)
    if protocol_version and protocol_version not in schema_title:
        msg = f"schema title does not contain protocol version {protocol_version}: {schema_title}"
        (errors if args.strict_schema_metadata else warnings).append(msg)

    for warning in warnings:
        print(f"WARNING: {warning}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"HQE protocol validation FAILED ({len(errors)} error(s)).", file=sys.stderr)
        return 1

    print(
        f"HQE protocol validation PASSED: protocol={protocol_version}, "
        f"schema={schema_version}, warnings={len(warnings)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
