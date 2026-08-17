"""Tests for truthful artifact wording and prioritization."""

import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from runtime import FindingRegistry, Finding, CodeEvidence, ArtifactPipeline


def _make_finding(fid, category="BUG", severity="MEDIUM", confidence="FACT", effort="S"):
    return Finding(
        id=fid,
        title=f"Finding {fid}",
        category=category,
        severity=severity,
        confidence=confidence,
        status="CONFIRMED",
        affected_component="src/x.py",
        observed_behavior="observed",
        expected_behavior="expected",
        root_cause="cause",
        impact="impact",
        remediation="fix it",
        effort=effort,
        regression_risk="Low",
        evidence=[CodeEvidence(path="src/x.py", start_line=1, end_line=1, snippet="x")],
    )


def _make_high_security_finding(fid, status="CONFIRMED"):
    ev = CodeEvidence(path="src/auth.rs", start_line=10, end_line=12, snippet="let key = \"insecure-static-key\";")
    return Finding(
        id=fid,
        title="Hardcoded Auth Key",
        category="SEC",
        severity="HIGH",
        confidence="FACT",
        status=status,
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
            "impact": "auth forgery",
        },
    )


def test_security_posture_softens_no_findings_claim():
    pipeline = ArtifactPipeline(FindingRegistry(), repo_name="test")
    text = pipeline.generate_security_posture()
    assert "No active security findings recorded" in text
    assert "not a guarantee" in text
    assert "No active security vulnerabilities detected" not in text


def test_unknowns_softens_no_unknowns_claim():
    pipeline = ArtifactPipeline(FindingRegistry(), repo_name="test")
    text = pipeline.generate_unknowns_verification()
    assert "No unverified hypotheses recorded" in text
    assert "Absence of recorded unknowns" in text
    assert "All findings verified" not in text


def test_pattern_group_requires_two_or_more():
    registry = FindingRegistry()
    registry.register(_make_finding("HQE-BUG-001", category="BUG"))
    pipeline = ArtifactPipeline(registry, repo_name="test")
    text = pipeline.generate_pattern_findings()
    assert "Pattern Group" not in text
    assert "two or more occurrences" in text


def test_pattern_group_shows_when_two_in_category():
    registry = FindingRegistry()
    registry.register(_make_finding("HQE-BUG-001", category="BUG"))
    registry.register(_make_finding("HQE-BUG-002", category="BUG"))
    pipeline = ArtifactPipeline(registry, repo_name="test")
    text = pipeline.generate_pattern_findings()
    assert "BUG Pattern Group (2 findings)" in text


def test_master_todo_prioritizes_severity_then_confidence_then_effort():
    registry = FindingRegistry()
    # Use severities that do not trigger HIGH/CRITICAL gates while still
    # exercising the severity > confidence > effort priority key.
    registry.register(_make_finding("HQE-BUG-001", severity="MEDIUM", confidence="FACT", effort="S"))
    registry.register(_make_finding("HQE-BUG-002", severity="MEDIUM", confidence="INFERENCE", effort="S"))
    registry.register(_make_finding("HQE-BUG-003", severity="LOW", confidence="FACT", effort="S"))
    registry.register(_make_finding("HQE-BUG-004", severity="MEDIUM", confidence="FACT", effort="M"))

    pipeline = ArtifactPipeline(registry, repo_name="test")
    text = pipeline.generate_master_todo()
    lines = [
        ln for ln in text.splitlines()
        if ln.startswith("|") and "Priority" not in ln and ":---" not in ln
    ]

    # Extract finding IDs in priority order.
    ordered = [ln.split("|")[2].strip() for ln in lines]
    assert ordered == ["HQE-BUG-001", "HQE-BUG-004", "HQE-BUG-002", "HQE-BUG-003"]


def test_incident_report_includes_active_high_security_findings():
    registry = FindingRegistry()
    registry.register(_make_high_security_finding("HQE-SEC-001"))
    pipeline = ArtifactPipeline(registry, repo_name="test")
    text = pipeline.generate_incident_mini_report()
    assert "HQE-SEC-001" in text
    assert "**Active Security Incidents:** 1" in text


def test_incident_report_excludes_verified_security_findings():
    registry = FindingRegistry()
    registry.register(_make_high_security_finding("HQE-SEC-001", status="VERIFIED"))
    pipeline = ArtifactPipeline(registry, repo_name="test")
    text = pipeline.generate_incident_mini_report()
    assert "HQE-SEC-001" not in text
    assert "No active CRITICAL/HIGH security incidents" in text


def test_incident_report_excludes_low_security_findings():
    registry = FindingRegistry()
    finding = _make_finding("HQE-SEC-001", category="SEC", severity="LOW")
    # SEC findings must carry a taint chain regardless of severity.
    finding.taint_chain = {
        "source": "auth.rs#L1",
        "transforms": ["comparator"],
        "validation_boundary": "auth module",
        "sink": "equality check",
        "impact": "minor side channel",
    }
    registry.register(finding)
    pipeline = ArtifactPipeline(registry, repo_name="test")
    text = pipeline.generate_incident_mini_report()
    assert "HQE-SEC-001" not in text
    assert "No active CRITICAL/HIGH security incidents" in text
