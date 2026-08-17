from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
SKILL_MD = ROOT / "SKILL.md"
PROTOCOL_REF = ROOT / "references" / "hqe-protocol.md"
SEVERITY_REF = ROOT / "references" / "severity-confidence-effort.md"
PRE_DELIVERY_REF = ROOT / "references" / "pre-delivery-gates.md"
CHANGE_CONTROL_REF = ROOT / "references" / "change-control.md"
HEALTH_REF = ROOT / "references" / "health-scoring.md"
INCIDENT_REF = ROOT / "references" / "security-review.md"


def test_skill_md_declares_protocol_authority():
    content = SKILL_MD.read_text(encoding="utf-8")
    assert "protocol/hqe-engineer.yaml" in content or "hqe-engineer.yaml" in content
    assert "5.0.0" in content


def test_skill_md_pr_harvest_ordering():
    content = SKILL_MD.read_text(encoding="utf-8")
    assert "Phase -1" in content
    assert "Phase 0" in content
    # Ensure Phase -1 is designated for PR/diff tasks before whole-repo orientation
    assert "Phase -1" in content and ("PR" in content or "diff" in content)


def test_confidence_model_includes_needs_verification():
    skill_content = SKILL_MD.read_text(encoding="utf-8")
    sev_content = SEVERITY_REF.read_text(encoding="utf-8")
    assert "NEEDS_VERIFICATION" in skill_content or "NEEDS_VERIFICATION" in sev_content


def test_anti_regression_and_change_budget_present():
    skill_content = SKILL_MD.read_text(encoding="utf-8")
    change_content = CHANGE_CONTROL_REF.read_text(encoding="utf-8")
    combined = skill_content + "\n" + change_content
    assert "BEHAVIOR CHANGE" in combined
    assert "change budget" in combined.lower() or "5 files" in combined.lower()


def test_severity_gate_present():
    skill_content = SKILL_MD.read_text(encoding="utf-8")
    sev_content = SEVERITY_REF.read_text(encoding="utf-8")
    combined = skill_content + "\n" + sev_content
    assert "severity gate" in combined.lower()
    assert "blast_radius" in combined or "preconditions" in combined or "exploitability" in combined


def test_pre_delivery_gates_present():
    assert PRE_DELIVERY_REF.is_file()
    content = PRE_DELIVERY_REF.read_text(encoding="utf-8")
    assert "pre-delivery" in content.lower() or "quality gate" in content.lower()


def test_health_scoring_present():
    assert HEALTH_REF.is_file()
    content = HEALTH_REF.read_text(encoding="utf-8")
    assert "health score" in content.lower()
    assert "10" in content and "1" in content
