import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from validate_semantics import validate_finding_semantics, validate_findings_file


def test_valid_finding_semantics():
    valid_finding = {
        "id": "HQE-SEC-001",
        "title": "Hardcoded JWT Secret",
        "category": "SEC",
        "severity": "HIGH",
        "confidence": "FACT",
        "status": "CONFIRMED",
        "affected_component": "auth.rs",
        "preconditions": ["Missing env var"],
        "exploitability": "High",
        "blast_radius": "Full auth bypass",
        "likelihood": "High",
        "likelihood_justification": "Common env omission",
        "exposure_evidence": "auth.rs#52",
        "taint_chain": {
            "source": "JWT_SECRET env",
            "transforms": ["unwrap_or_else"],
            "validation_boundary": "JWT verify",
            "sink": "DecodingKey::from_secret",
            "impact": "Auth token forgery"
        },
        "evidence": [
            {
                "path": "crates/hqe-core/src/auth.rs",
                "start_line": 52,
                "end_line": 56,
                "snippet": "let secret = std::env::var(\"JWT_SECRET\").unwrap_or_else(...);"
            }
        ],
        "observed_behavior": "Fallback to dev secret",
        "expected_behavior": "Fail fast",
        "root_cause": "Permissive fallback",
        "impact": "Auth forgery",
        "remediation": "Fail fast",
        "validation": ["cargo test"],
        "effort": "S",
        "regression_risk": "Low"
    }

    errors = validate_finding_semantics(valid_finding, 0)
    assert not errors, f"Unexpected errors: {errors}"


def test_category_id_mismatch_fails():
    finding = {
        "id": "HQE-SEC-001",
        "category": "BUG",  # Mismatch: SEC vs BUG
        "severity": "MEDIUM",
        "evidence": [{"path": "a.py", "start_line": 1, "end_line": 2, "snippet": "x = 1"}]
    }
    errors = validate_finding_semantics(finding, 0)
    assert any("does not match 'category' field" in err for err in errors)


def test_critical_without_severity_gate_fails():
    finding = {
        "id": "HQE-BUG-001",
        "category": "BUG",
        "severity": "CRITICAL",
        "evidence": [{"path": "a.py", "start_line": 1, "end_line": 2, "snippet": "x = 1"}]
        # Missing preconditions, blast_radius, exploitability, likelihood, etc.
    }
    errors = validate_finding_semantics(finding, 0)
    assert any("severity-gate field" in err for err in errors)


def test_invalid_line_numbers_rejected():
    finding = {
        "id": "HQE-BUG-002",
        "category": "BUG",
        "severity": "LOW",
        "evidence": [{"path": "a.py", "start_line": 50, "end_line": 40, "snippet": "x = 1"}]  # end < start
    }
    errors = validate_finding_semantics(finding, 0)
    assert any("end_line' must be integer >= start_line" in err for err in errors)


def test_empty_snippet_rejected():
    finding = {
        "id": "HQE-BUG-003",
        "category": "BUG",
        "severity": "LOW",
        "evidence": [{"path": "a.py", "start_line": 1, "end_line": 2, "snippet": "   "}]  # empty
    }
    errors = validate_finding_semantics(finding, 0)
    assert any("'snippet' must be non-empty" in err for err in errors)
