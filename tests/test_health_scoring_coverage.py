"""Tests for coverage-aware health scoring."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from runtime import (
    FindingRegistry,
    Finding,
    CodeEvidence,
    HealthScore,
    compute_health_score,
    score_from_findings,
    score_to_band,
)


def _make_finding(fid, severity):
    return Finding(
        id=fid,
        title=f"Finding {fid}",
        category="BUG",
        severity=severity,
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
        evidence=[CodeEvidence(path="src/x.py", start_line=1, end_line=1, snippet="x")],
    )


def test_empty_registry_unknown_coverage_omits_score():
    registry = FindingRegistry()
    result = registry.health_score()
    assert isinstance(result, HealthScore)
    assert result.omitted is True
    assert result.score is None
    assert "false-perfect" in " ".join(result.reasons).lower()


def test_known_coverage_with_no_findings_returns_perfect():
    registry = FindingRegistry()
    result = registry.health_score(coverage_known=True, coverage_depth="full")
    assert result.omitted is False
    assert result.score == 10
    assert any("full" in r for r in result.reasons)


def test_unknown_coverage_with_findings_reports_numeric_score():
    registry = FindingRegistry()
    # Two MEDIUM findings: 100 - 8 - 8 = 84 → maps to 8.
    registry.register(_make_finding("HQE-BUG-001", "MEDIUM"))
    registry.register(_make_finding("HQE-BUG-002", "MEDIUM"))
    result = registry.health_score()
    assert result.omitted is False
    assert result.score == 8


def test_multiple_findings_score():
    registry = FindingRegistry()
    for i, severity in enumerate(["MEDIUM", "MEDIUM", "LOW", "LOW", "INFO"]):
        registry.register(_make_finding(f"HQE-BUG-{i+1:03d}", severity))
    result = registry.health_score(coverage_known=True, coverage_depth="partial")
    assert result.score is not None
    assert result.score >= 1
    assert result.score <= 10


def test_unreviewed_surfaces_are_recorded_in_reasons():
    registry = FindingRegistry()
    surfaces = ["src/legacy.py", "tests/manual"]
    result = registry.health_score(
        coverage_known=True, coverage_depth="partial", unreviewed_surfaces=surfaces
    )
    assert result.omitted is False
    assert any("unreviewed" in r.lower() for r in result.reasons)
    assert any(str(len(surfaces)) in r for r in result.reasons)


def test_score_from_findings_empty_is_perfect():
    assert score_from_findings([]) == 10


def test_score_to_band_mappings():
    assert score_to_band(10) == "Exceptional"
    assert score_to_band(8) == "Solid"
    assert score_to_band(6) == "Adequate"
    assert score_to_band(4) == "Concerning"
    assert score_to_band(2) == "Critical Risk"


def test_compute_health_score_returns_health_score_dataclass():
    result = compute_health_score([], coverage_known=True)
    assert isinstance(result, HealthScore)
    assert result.to_dict()["omitted"] is False
