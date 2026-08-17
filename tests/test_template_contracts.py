from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
TEMPLATES_DIR = ROOT / "templates"


def test_all_templates_exist_and_formatted():
    expected_templates = [
        "finding.md", "report.md", "handoff.md", "run-manifest.md",
        "risk-register.md", "master-todo-backlog.md", "pattern-findings.md",
        "quick-wins-vs-structural.md", "security-posture-summary.md",
        "reliability-summary.md", "testing-gaps.md", "unknowns-verification.md",
        "confidence-declaration.md", "session-log.md", "redaction-log.md",
        "patch-action.md", "remediation-plan.md", "validation-report.md",
        "incident-mini-report.md"
    ]
    for tmpl in expected_templates:
        p = TEMPLATES_DIR / tmpl
        assert p.is_file(), f"Missing template file: {tmpl}"
        content = p.read_text(encoding="utf-8")
        assert len(content.strip()) > 10, f"Template {tmpl} is empty"
