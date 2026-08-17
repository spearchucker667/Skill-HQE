"""Schema-level validation tests for Skill-HQE artifacts."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from jsonschema import Draft7Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "schemas"


def test_every_schema_is_valid_draft7():
    for schema_file in SCHEMAS.glob("*.schema.json"):
        schema = json.loads(schema_file.read_text(encoding="utf-8"))
        Draft7Validator.check_schema(schema)
        assert schema.get("$schema") == "http://json-schema.org/draft-07/schema#"


def test_every_template_has_a_schema():
    templates = {p.stem for p in (ROOT / "templates").glob("*.md")}
    schemas = {p.stem.replace(".schema", "") for p in SCHEMAS.glob("*.schema.json")}

    # Mapping for templates whose names differ from schema stems.
    mapped = {
        "master-todo-backlog": "master-todo",
        "security-posture-summary": "security-posture",
        "unknowns-verification": "unknowns",
    }
    missing = []
    for tmpl in templates:
        key = mapped.get(tmpl, tmpl)
        if key not in schemas and key != "report":  # report uses findings schema
            missing.append(tmpl)
    assert not missing, f"Templates without schemas: {missing}"
