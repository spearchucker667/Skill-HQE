import json
import sys
import tempfile
from pathlib import Path
import pytest
from jsonschema import validate

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from runtime import (
    SessionManager, SessionState,
    FindingRegistry, Finding,
    EvidenceStore, CodeEvidence,
    RunManifestGenerator,
    ArtifactPipeline,
    TypedRedactionEngine,
    classify_secret
)

SCHEMAS = ROOT / "schemas"


def _load_schema(name: str):
    return json.loads((SCHEMAS / name).read_text(encoding="utf-8"))


def test_session_manager_lifecycle():
    with tempfile.TemporaryDirectory() as tmpdir:
        log_path = Path(tmpdir) / "HQE_SESSION_LOG.json"
        sm = SessionManager(repo_path=tmpdir)
        assert sm.state == SessionState.INIT

        sm.transition_to(SessionState.ORIENTED, "Orientation complete")
        assert sm.state == SessionState.ORIENTED

        sm.mark_in_progress("Review auth handlers")
        sm.add_discovered("HQE-SEC-001")
        sm.mark_completed("Review auth handlers")
        sm.add_next_session("Fix JWT secret fallback")
        sm.finish()

        assert sm.state == SessionState.COMPLETED
        assert sm.ended_at is not None

        out = sm.save_to_file(log_path)
        assert out.is_file()

        # Validate against schema
        schema = _load_schema("session-log.schema.json")
        data = json.loads(out.read_text(encoding="utf-8"))
        validate(instance=data, schema=schema)


def test_finding_registry_and_severity_gate():
    registry = FindingRegistry()

    ev = CodeEvidence(
        path="src/auth.rs",
        start_line=10,
        end_line=12,
        snippet="let key = \"insecure-static-key\";"
    )

    finding = Finding(
        id="HQE-SEC-001",
        title="Hardcoded Auth Key",
        category="SEC",
        severity="HIGH",
        confidence="FACT",
        status="CONFIRMED",
        affected_component="src/auth.rs",
        observed_behavior="Uses static key",
        expected_behavior="Must read env",
        root_cause="Dev hardcoding",
        impact="Token forgery",
        remediation="Use env var",
        effort="S",
        regression_risk="Low",
        evidence=[ev],
        preconditions=["Dev mode active"],
        exploitability="High",
        blast_radius="System wide",
        likelihood="High",
        likelihood_justification="Default config",
        exposure_evidence="src/auth.rs:10",
        taint_chain={
            "source": "auth.rs#L10",
            "transforms": ["key parser"],
            "validation_boundary": "token validator",
            "sink": "jwt verify",
            "impact": "auth forgery"
        }
    )

    registry.register(finding)
    assert registry.get("HQE-SEC-001") is not None
    assert registry.count_by_severity()["HIGH"] == 1

    # Transition status (FIXED requires verification evidence)
    registry.transition_status(
        "HQE-SEC-001", "FIXED",
        verification_evidence=["commit abc123", "pytest tests/test_runtime.py::test_finding_registry_and_severity_gate"]
    )
    assert registry.get("HQE-SEC-001").status == "FIXED"


def test_evidence_store_and_redaction():
    store = EvidenceStore()
    ev = store.add_evidence(
        path="config/keys.py",
        snippet="AKIA1234567890ABCDEF",
        start_line=1,
        end_line=1
    )
    assert "AKIA" not in ev.snippet
    assert "REDACTED_AWS_ACCESS_KEY" in ev.snippet

    record = store.record_tool_execution(
        tool_name="pytest",
        command="pytest tests/",
        exit_code=0,
        stdout="Passed with token xoxb-1234567890-123456789012"
    )
    assert "xoxb-" not in record["stdout"]
    assert "REDACTED_SLACK_TOKEN" in record["stdout"]


def test_run_manifest_generator():
    with tempfile.TemporaryDirectory() as tmpdir:
        registry = FindingRegistry()
        gen = RunManifestGenerator(repo_path=tmpdir, mode="audit")
        manifest = gen.build_manifest(registry=registry, total_files=10, health_score=8)

        schema = _load_schema("run-manifest.schema.json")
        validate(instance=manifest, schema=schema)


def test_artifact_pipeline_generation():
    with tempfile.TemporaryDirectory() as tmpdir:
        registry = FindingRegistry()
        ev = CodeEvidence(path="src/main.rs", start_line=1, end_line=2, snippet="fn main() {}")
        f = Finding(
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
            validation=["cargo test"]
        )
        registry.register(f)

        pipeline = ArtifactPipeline(registry, repo_name="test-repo")
        artifacts = pipeline.build_all_artifacts(output_dir=tmpdir)

        expected_files = {
            "RISK_REGISTER.md",
            "MASTER_TODO_BACKLOG.md",
            "PATTERN_FINDINGS.md",
            "QUICK_WINS_VS_STRUCTURAL.md",
            "SECURITY_POSTURE_SUMMARY.md",
            "RELIABILITY_SUMMARY.md",
            "TESTING_GAPS.md",
            "UNKNOWNS_VERIFICATION.md",
            "CONFIDENCE_DECLARATION.md",
            "INCIDENT_MINI_REPORT.md",
            "PATCH_ACTIONS.md",
            "REMEDIATION_PLAN.md",
            "VALIDATION_REPORT.md"
        }
        for ef in expected_files:
            assert ef in artifacts
            assert artifacts[ef].is_file()
            assert len(artifacts[ef].read_text(encoding="utf-8")) > 10


def test_health_score_bounds():
    registry = FindingRegistry()
    # Unknown coverage with no findings must not claim a perfect score.
    score = registry.health_score()
    assert score.omitted is True
    assert score.score is None

    ev = CodeEvidence(path="src/x.py", start_line=1, end_line=1, snippet="x")
    for i in range(5):
        registry.register(Finding(
            id=f"HQE-BUG-{i+1:03d}",
            title=f"Bug {i}",
            category="BUG",
            severity="CRITICAL",
            confidence="FACT",
            status="CONFIRMED",
            affected_component="src/x.py",
            observed_behavior="crash",
            expected_behavior="ok",
            root_cause="missing check",
            impact="high",
            remediation="add check",
            effort="S",
            regression_risk="Low",
            evidence=[ev],
            preconditions=["default config"],
            exploitability="High",
            blast_radius="System wide",
            likelihood="High",
            likelihood_justification="default path",
            exposure_evidence="src/x.py:1"
        ))
    # With findings present the numeric score is reported even if coverage is unknown.
    score = registry.health_score()
    assert score.omitted is False
    assert score.score == 2  # maps to Broken band (1-2)


def test_typed_redaction_engine():
    engine = TypedRedactionEngine()
    text = "key = AKIA1234567890ABCDEF and slack = xoxb-1234567890-123456789012"
    redacted = engine.redact(text, file_path="config.py")
    assert "AKIA" not in redacted
    assert "xoxb-" not in redacted
    summary = engine.typed_summary()
    assert summary["total_redactions"] == 2
    categories = {e["category"] for e in summary["typed_entries"]}
    assert "api_key" in categories
    assert "token" in categories


def test_classify_secret():
    assert classify_secret("AKIA1234567890ABCDEF") == "api_key"
    assert classify_secret("xoxb-1234567890-123456789012") == "token"
    assert classify_secret("postgres://user:pass@host/db") == "database_url"
