"""Protocol-level validation tests for Skill-HQE."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]


def test_protocol_yaml_is_valid_against_schema():
    schema_path = ROOT / "protocol" / "hqe-engineer-schema.json"
    protocol_path = ROOT / "protocol" / "hqe-engineer.yaml"

    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    protocol = yaml.safe_load(protocol_path.read_text(encoding="utf-8"))

    from jsonschema import validate
    validate(instance=protocol, schema=schema)


def test_protocol_version_matches_version_file():
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    protocol = yaml.safe_load((ROOT / "protocol" / "hqe-engineer.yaml").read_text(encoding="utf-8"))

    assert protocol.get("protocol_version") == version
    assert protocol.get("schema_version") == version


def test_protocol_has_required_sections():
    protocol = yaml.safe_load((ROOT / "protocol" / "hqe-engineer.yaml").read_text(encoding="utf-8"))

    required = [
        "schema_version",
        "protocol_version",
        "definitions",
        "role",
        "phases",
        "control_plane_requirements",
    ]
    for key in required:
        assert key in protocol, f"Missing required protocol section: {key}"

    definitions = protocol.get("definitions", {})
    assert "severity_levels" in definitions
    assert "confidence_tags" in definitions
    assert "health_score_rubric" in definitions


def test_protocol_validators_run_cleanly():
    import subprocess
    result = subprocess.run(
        ["python3", "protocol/validate.py", "protocol/hqe-engineer.yaml"],
        cwd=ROOT,
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, result.stdout + result.stderr
