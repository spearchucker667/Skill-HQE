"""Finding/CodeEvidence from_dict round-trip and FindingRegistry.load_many tests."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from runtime import FindingRegistry, Finding, CodeEvidence

FIXTURE = ROOT / "tests" / "fixtures" / "sample_finding_valid.json"


def _sample_finding() -> Finding:
    ev = CodeEvidence(
        path="src/x.py",
        snippet="x",
        start_line=1,
        end_line=1,
        verified=True,
        verification_method="disk_verify",
        source_hash="abc123",
    )
    return Finding(
        id="HQE-BUG-001",
        title="Missing null check",
        category="BUG",
        severity="MEDIUM",
        confidence="FACT",
        status="CONFIRMED",
        affected_component="src/x.py",
        observed_behavior="Crash on null input",
        expected_behavior="Graceful handling",
        root_cause="Missing check",
        impact="Process termination",
        remediation="Add null check",
        effort="S",
        regression_risk="Low",
        evidence=[ev],
        validation=[],
        related_findings=[],
    )


def test_from_dict_roundtrip_preserves_all_fields():
    f = _sample_finding()
    loaded = Finding.from_dict(f.to_dict())
    assert loaded == f


def test_roundtrip_preserves_evidence_verification_state():
    f = _sample_finding()
    loaded = Finding.from_dict(f.to_dict())
    ev = loaded.evidence[0]
    assert ev.verified is True
    assert ev.verification_method == "disk_verify"
    assert ev.source_hash == "abc123"


def test_code_evidence_from_dict_reads_all_fields():
    ev = CodeEvidence.from_dict(
        {
            "path": "src/a.py",
            "snippet": "x",
            "start_line": 3,
            "end_line": 5,
            "symbol": "foo",
            "anchor": "foo",
            "grep_signature": "def foo",
            "verified": True,
            "verification_method": "disk_verify",
            "verified_at": "2026-08-17T00:00:00Z",
            "source_hash": "deadbeef",
        }
    )
    assert ev.verified is True
    assert ev.verification_method == "disk_verify"
    assert ev.source_hash == "deadbeef"
    assert ev.start_line == 3


def test_from_dict_lenient_defaults():
    loaded = Finding.from_dict({})
    assert loaded.id == ""
    assert loaded.confidence == "FACT"
    assert loaded.status == "CONFIRMED"
    assert loaded.effort == "S"
    assert loaded.regression_risk == "Low"
    assert loaded.evidence == []
    assert loaded.validation == []
    assert loaded.related_findings == []


def test_fixture_roundtrip_through_registry():
    raw_list = json.loads(FIXTURE.read_text(encoding="utf-8"))
    registry = FindingRegistry()
    loaded = registry.load_many(raw_list)
    assert len(loaded) == 1
    assert registry.get("HQE-SEC-001") == loaded[0]
    data = loaded[0].to_dict()
    assert data["validation"] == [
        "cargo test --package hqe-core test_auth_missing_secret_fails"
    ]
    assert data["related_findings"] == []


def test_load_many_rejects_invalid_finding():
    registry = FindingRegistry()
    with pytest.raises(ValueError):
        registry.load_many([{"id": "not-a-finding-id"}])


def test_load_many_registers_in_order():
    registry = FindingRegistry()
    a = _sample_finding()
    b = _sample_finding()
    b.id = "HQE-BUG-002"
    loaded = registry.load_many([a.to_dict(), b.to_dict()])
    assert [f.id for f in loaded] == ["HQE-BUG-001", "HQE-BUG-002"]
    assert len(registry.findings) == 2
