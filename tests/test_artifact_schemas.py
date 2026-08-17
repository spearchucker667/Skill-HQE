"""Tests that generated artifact JSON validates against canonical schemas."""

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
    TypedRedactionEngine,
)

SCHEMAS = ROOT / "schemas"


def _load_schema(name: str) -> dict:
    path = SCHEMAS / name
    assert path.is_file(), f"Missing schema {name}"
    return json.loads(path.read_text(encoding="utf-8"))


def _build_registry() -> FindingRegistry:
    registry = FindingRegistry()
    ev = CodeEvidence(path="src/main.rs", start_line=1, end_line=2, snippet="fn main() {}")
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
        evidence=[ev],
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
        evidence=[CodeEvidence(path="src/auth.rs", start_line=10, end_line=10, snippet="let key = \"secret\";")],
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


def test_patch_actions_json_schema():
    registry = _build_registry()
    pipeline = ArtifactPipeline(registry, repo_name="test-repo")
    data = pipeline.generate_patch_actions_json()

    patch_action_schema = _load_schema("patch-action.schema.json")
    for action in data["patch_actions"]:
        validate(instance=action, schema=patch_action_schema)

    collection_schema = _load_schema("patch-actions.schema.json")
    registry_resources = Registry().with_resource(
        "patch-action.schema.json", Resource.from_contents(patch_action_schema)
    )
    validate(instance=data, schema=collection_schema, registry=registry_resources)


def test_remediation_plan_json_schema():
    registry = _build_registry()
    pipeline = ArtifactPipeline(registry, repo_name="test-repo")
    data = pipeline.generate_remediation_plan_json()

    remediation_schema = _load_schema("remediation-plan.schema.json")
    patch_action_schema = _load_schema("patch-action.schema.json")
    registry_resources = Registry().with_resource(
        "patch-action.schema.json", Resource.from_contents(patch_action_schema)
    )
    validate(instance=data, schema=remediation_schema, registry=registry_resources)


def test_validation_report_json_schema():
    registry = _build_registry()
    pipeline = ArtifactPipeline(registry, repo_name="test-repo")
    data = pipeline.generate_validation_report_json()

    schema = _load_schema("validation-report.schema.json")
    validate(instance=data, schema=schema)


def test_redaction_log_json_schema_empty():
    registry = _build_registry()
    session = SessionManager(repo_path=".")
    pipeline = ArtifactPipeline(registry, session=session, repo_name="test-repo")
    data = pipeline.generate_redaction_log_json()

    schema = _load_schema("redaction-log.schema.json")
    validate(instance=data, schema=schema)
    assert data["total_redactions"] == 0


def test_redaction_log_json_schema_with_engine():
    registry = _build_registry()
    session = SessionManager(repo_path=".")
    engine = TypedRedactionEngine()
    engine.redact("key = AKIA1234567890ABCDEF", file_path="config/keys.py")
    engine.redact("slack = xoxb-1234567890-123456789012", file_path="services/notifier.py")

    pipeline = ArtifactPipeline(registry, session=session, repo_name="test-repo", redaction_engine=engine)
    data = pipeline.generate_redaction_log_json()

    schema = _load_schema("redaction-log.schema.json")
    validate(instance=data, schema=schema)
    assert data["total_redactions"] == 2
    assert data["run_id"] == session.session_id


def test_artifact_pipeline_writes_json_artifacts():
    with tempfile.TemporaryDirectory() as tmpdir:
        registry = _build_registry()
        session = SessionManager(repo_path=tmpdir)
        engine = TypedRedactionEngine()
        engine.redact("key = AKIA1234567890ABCDEF", file_path="config/keys.py")

        pipeline = ArtifactPipeline(registry, session=session, repo_name="test-repo", redaction_engine=engine)
        artifacts = pipeline.build_all_artifacts(output_dir=tmpdir)

        for name in ("PATCH_ACTIONS.json", "REMEDIATION_PLAN.json", "VALIDATION_REPORT.json", "REDACTION_LOG.json"):
            assert name in artifacts, f"Missing artifact {name}"
            assert artifacts[name].is_file()
            # Verify valid JSON and non-empty content.
            payload = json.loads(artifacts[name].read_text(encoding="utf-8"))
            assert payload

        # Also verify the new markdown deliverable is written.
        assert "REDACTION_LOG.md" in artifacts
        assert artifacts["REDACTION_LOG.md"].is_file()


def test_artifact_pipeline_json_files_validate_against_schemas():
    with tempfile.TemporaryDirectory() as tmpdir:
        registry = _build_registry()
        session = SessionManager(repo_path=tmpdir)
        engine = TypedRedactionEngine()
        engine.redact("key = AKIA1234567890ABCDEF", file_path="config/keys.py")

        pipeline = ArtifactPipeline(registry, session=session, repo_name="test-repo", redaction_engine=engine)
        artifacts = pipeline.build_all_artifacts(output_dir=tmpdir)

        patch_action_schema = _load_schema("patch-action.schema.json")
        patch_actions_schema = _load_schema("patch-actions.schema.json")
        remediation_schema = _load_schema("remediation-plan.schema.json")
        validation_schema = _load_schema("validation-report.schema.json")
        redaction_schema = _load_schema("redaction-log.schema.json")

        registry_resources = (
            Registry()
            .with_resource("patch-action.schema.json", Resource.from_contents(patch_action_schema))
        )

        validate(
            instance=json.loads(artifacts["PATCH_ACTIONS.json"].read_text(encoding="utf-8")),
            schema=patch_actions_schema,
            registry=registry_resources,
        )
        validate(
            instance=json.loads(artifacts["REMEDIATION_PLAN.json"].read_text(encoding="utf-8")),
            schema=remediation_schema,
            registry=registry_resources,
        )
        validate(
            instance=json.loads(artifacts["VALIDATION_REPORT.json"].read_text(encoding="utf-8")),
            schema=validation_schema,
        )
        validate(
            instance=json.loads(artifacts["REDACTION_LOG.json"].read_text(encoding="utf-8")),
            schema=redaction_schema,
        )
