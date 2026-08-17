from pathlib import Path
import json
import pytest
from jsonschema import Draft7Validator, validate, ValidationError
from referencing import Registry, Resource

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "schemas"
FIXTURES = ROOT / "tests" / "fixtures"


def _load_schema(name: str):
    path = SCHEMAS / name
    assert path.is_file(), f"Missing schema {name}"
    return json.loads(path.read_text(encoding="utf-8"))


def _load_fixture(name: str):
    path = FIXTURES / name
    assert path.is_file(), f"Missing fixture {name}"
    return json.loads(path.read_text(encoding="utf-8"))


def test_all_schemas_are_valid_draft7():
    for schema_file in SCHEMAS.glob("*.schema.json"):
        schema = json.loads(schema_file.read_text(encoding="utf-8"))
        Draft7Validator.check_schema(schema)


def test_finding_valid_fixture():
    findings_schema = _load_schema("findings.schema.json")
    finding_schema = _load_schema("finding.schema.json")
    data = _load_fixture("sample_finding_valid.json")

    registry = Registry().with_resource("finding.schema.json", Resource.from_contents(finding_schema))
    validate(instance=data, schema=findings_schema, registry=registry)


def test_finding_invalid_fixture_fails():
    findings_schema = _load_schema("findings.schema.json")
    finding_schema = _load_schema("finding.schema.json")
    data = _load_fixture("sample_finding_invalid.json")

    registry = Registry().with_resource("finding.schema.json", Resource.from_contents(finding_schema))
    with pytest.raises(ValidationError):
        validate(instance=data, schema=findings_schema, registry=registry)


def test_run_manifest_fixture():
    manifest_schema = _load_schema("run-manifest.schema.json")
    data = _load_fixture("sample_manifest.json")
    validate(instance=data, schema=manifest_schema)


def test_handoff_fixture():
    handoff_schema = _load_schema("handoff.schema.json")
    finding_schema = _load_schema("finding.schema.json")
    data = _load_fixture("sample_handoff.json")

    registry = Registry().with_resource("finding.schema.json", Resource.from_contents(finding_schema))
    validate(instance=data, schema=handoff_schema, registry=registry)


def test_session_log_fixture():
    session_schema = _load_schema("session-log.schema.json")
    data = _load_fixture("sample_session_log.json")
    validate(instance=data, schema=session_schema)


def test_redaction_log_fixture():
    redaction_schema = _load_schema("redaction-log.schema.json")
    data = _load_fixture("sample_redaction_log.json")
    validate(instance=data, schema=redaction_schema)


def test_report_schema_fixture():
    report_schema = _load_schema("report.schema.json")
    finding_schema = _load_schema("finding.schema.json")
    data = _load_fixture("sample_report.json")

    registry = Registry().with_resource("finding.schema.json", Resource.from_contents(finding_schema))
    validate(instance=data, schema=report_schema, registry=registry)
