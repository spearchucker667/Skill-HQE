"""Tests for the REPORT.json artifact and report.schema.json contract."""

import json
import sys
import tempfile
from pathlib import Path

import pytest
from jsonschema import validate
from referencing import Registry, Resource

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from runtime import (
    ArtifactPipeline,
    CodeEvidence,
    Finding,
    FindingRegistry,
    SessionManager,
)

SCHEMAS = ROOT / "schemas"


def _load_schema(name: str) -> dict:
    path = SCHEMAS / name
    assert path.is_file(), f"Missing schema {name}"
    return json.loads(path.read_text(encoding="utf-8"))


def _build_registry() -> FindingRegistry:
    registry = FindingRegistry()
    registry.register(Finding(
        id="HQE-BUG-001",
        title="Logic Error in Main",
        category="BUG",
        severity="MEDIUM",
        confidence="FACT",
        status="CONFIRMED",
        affected_component="src/main.rs",
        observed_behavior="Crash",
        expected_behavior="Success",
        root_cause="Missing check",
        impact="Process termination",
        remediation="Add null check",
        effort="S",
        regression_risk="Low",
        evidence=[CodeEvidence(path="src/main.rs", start_line=1, end_line=2, snippet="fn main() {}")],
        validation=["cargo test"],
    ))
    registry.register(Finding(
        id="HQE-SEC-001",
        title="Hardcoded Secret",
        category="SEC",
        severity="HIGH",
        confidence="FACT",
        status="CONFIRMED",
        affected_component="src/auth.rs",
        observed_behavior="Static secret in source",
        expected_behavior="Read from environment",
        root_cause="Developer convenience",
        impact="Credential exposure",
        remediation="Use env var",
        effort="S",
        regression_risk="Low",
        evidence=[CodeEvidence(path="src/auth.rs", start_line=10, end_line=10, snippet='let key = "secret";')],
        validation=["pytest tests/test_auth.py"],
        preconditions=["Default build"],
        exploitability="High",
        blast_radius="All users",
        likelihood="High",
        likelihood_justification="Default config exposes it",
        exposure_evidence="src/auth.rs:10",
        taint_chain={
            "source": "src/auth.rs#L10",
            "transforms": ["key parser"],
            "validation_boundary": "token validator",
            "sink": "jwt verify",
            "impact": "auth forgery",
        },
    ))
    return registry


def test_report_json_schema():
    registry = _build_registry()
    session = SessionManager(repo_path=".")
    pipeline = ArtifactPipeline(registry, session=session, repo_name="test-repo")
    data = pipeline.generate_report_json()

    report_schema = _load_schema("report.schema.json")
    finding_schema = _load_schema("finding.schema.json")
    registry_resources = Registry().with_resource(
        "finding.schema.json", Resource.from_contents(finding_schema)
    )
    validate(instance=data, schema=report_schema, registry=registry_resources)

    assert data["run_id"] == session.session_id
    assert data["protocol_version"]
    assert data["repository"]["name"] == "test-repo"
    assert data["executive_summary"]["critical_count"] == 0
    assert data["executive_summary"]["high_count"] == 1
    assert data["executive_summary"]["medium_count"] == 1
    assert len(data["findings"]) == 2


def test_report_json_top_priorities_and_blockers():
    registry = _build_registry()
    pipeline = ArtifactPipeline(registry, repo_name="test-repo")
    data = pipeline.generate_report_json()

    priorities = data["executive_summary"]["top_priorities"]
    blockers = data["executive_summary"]["blockers"]
    assert any("HQE-SEC-001" in p for p in priorities)
    assert any("HQE-SEC-001" in b for b in blockers)
    assert priorities[0].startswith("HQE-SEC-001")


def test_report_json_empty_registry():
    registry = FindingRegistry()
    pipeline = ArtifactPipeline(registry, repo_name="empty-repo")
    data = pipeline.generate_report_json()

    report_schema = _load_schema("report.schema.json")
    finding_schema = _load_schema("finding.schema.json")
    registry_resources = Registry().with_resource(
        "finding.schema.json", Resource.from_contents(finding_schema)
    )
    validate(instance=data, schema=report_schema, registry=registry_resources)

    assert data["executive_summary"]["critical_count"] == 0
    assert data["executive_summary"]["high_count"] == 0
    # An empty audit with unknown coverage must not claim a false-perfect score.
    assert data["health_score"]["omitted"] is True
    assert data["health_score"]["score"] is None
    assert data["health_score"]["band"] == "Unknown"
    assert len(data["findings"]) == 0


def test_build_all_artifacts_includes_report_json():
    with tempfile.TemporaryDirectory() as tmpdir:
        registry = _build_registry()
        session = SessionManager(repo_path=tmpdir)
        pipeline = ArtifactPipeline(registry, session=session, repo_name="test-repo")
        artifacts = pipeline.build_all_artifacts(output_dir=tmpdir)

        assert "REPORT.json" in artifacts
        assert artifacts["REPORT.json"].is_file()
        payload = json.loads(artifacts["REPORT.json"].read_text(encoding="utf-8"))
        assert payload["run_id"] == session.session_id
        assert len(payload["findings"]) == 2
