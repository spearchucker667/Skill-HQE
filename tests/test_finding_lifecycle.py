"""Finding registry lifecycle, duplicate-ID, and transition-rule tests."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from runtime import FindingRegistry, Finding, CodeEvidence


def _make_finding(fid: str, status: str = "CONFIRMED", severity: str = "MEDIUM") -> Finding:
    ev = CodeEvidence(path="src/main.py", snippet="buggy line", start_line=1, end_line=1)
    return Finding(
        id=fid,
        title=f"Finding {fid}",
        category="BUG",
        severity=severity,
        confidence="FACT",
        status=status,
        affected_component="src/main.py",
        observed_behavior="observed",
        expected_behavior="expected",
        root_cause="cause",
        impact="impact",
        remediation="fix",
        effort="S",
        regression_risk="Low",
        evidence=[ev]
    )


def test_duplicate_register_rejected():
    registry = FindingRegistry()
    f1 = _make_finding("HQE-BUG-001")
    f2 = _make_finding("HQE-BUG-001")
    registry.register(f1)
    with pytest.raises(ValueError, match="already registered"):
        registry.register(f2)


def test_explicit_update_works():
    registry = FindingRegistry()
    f = _make_finding("HQE-BUG-001")
    registry.register(f)
    registry.update("HQE-BUG-001", title="Updated title")
    assert registry.get("HQE-BUG-001").title == "Updated title"


def test_update_rejects_status_change():
    registry = FindingRegistry()
    f = _make_finding("HQE-BUG-001", status="OPEN")
    registry.register(f)
    with pytest.raises(ValueError, match="transition_status"):
        registry.update("HQE-BUG-001", status="VERIFIED")


def test_update_rejects_id_change():
    registry = FindingRegistry()
    f = _make_finding("HQE-BUG-001")
    registry.register(f)
    with pytest.raises(ValueError, match="immutable"):
        registry.update("HQE-BUG-001", id="HQE-BUG-999")


def test_invalid_status_transition_rejected():
    registry = FindingRegistry()
    f = _make_finding("HQE-BUG-001", status="OPEN")
    registry.register(f)
    # Unknown statuses are rejected outright.
    with pytest.raises(ValueError, match="Invalid finding status"):
        registry.transition_status("HQE-BUG-001", "SUSPECTED")
    # Transitions not present in the v5 transition graph are rejected.
    with pytest.raises(ValueError, match="invalid transition"):
        registry.transition_status("HQE-BUG-001", "VERIFIED")


def test_valid_status_transition_accepted():
    registry = FindingRegistry()
    f = _make_finding("HQE-BUG-001", status="CONFIRMED")
    registry.register(f)
    registry.transition_status("HQE-BUG-001", "VERIFIED", verification_evidence=["pytest test_bug"])
    assert registry.get("HQE-BUG-001").status == "VERIFIED"


def test_verified_requires_verification_evidence():
    registry = FindingRegistry()
    f = _make_finding("HQE-BUG-001", status="CONFIRMED")
    registry.register(f)
    with pytest.raises(ValueError, match="verification evidence"):
        registry.transition_status("HQE-BUG-001", "VERIFIED")


def test_supersede_preserves_history_and_successor():
    registry = FindingRegistry()
    f1 = _make_finding("HQE-BUG-001", status="CONFIRMED")
    registry.register(f1)
    f2 = _make_finding("HQE-BUG-002", status="CONFIRMED")
    registry.register(f2)
    registry.supersede("HQE-BUG-001", "HQE-BUG-002", reason="consolidated")
    assert registry.get("HQE-BUG-001").status == "DEFERRED"
    # Successor relationship is recorded on the deferred finding.
    assert "HQE-BUG-002" in registry.get("HQE-BUG-001").related_findings
    history = registry.get_history("HQE-BUG-001")
    assert any(entry["to_status"] == "DEFERRED" for entry in history)
    assert any(entry.get("reason") == "consolidated" for entry in history)


def test_reopen_verified_requires_reason():
    registry = FindingRegistry()
    f = _make_finding("HQE-BUG-001", status="CONFIRMED")
    registry.register(f)
    registry.transition_status("HQE-BUG-001", "VERIFIED", verification_evidence=["pytest"])
    with pytest.raises(ValueError, match="reason"):
        registry.transition_status("HQE-BUG-001", "OPEN")
    registry.transition_status("HQE-BUG-001", "OPEN", reason="regression observed")
    assert registry.get("HQE-BUG-001").status == "OPEN"
