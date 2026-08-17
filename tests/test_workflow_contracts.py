from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS_DIR = ROOT / "workflows"


def test_all_workflows_exist_and_non_empty():
    expected_workflows = [
        "full-audit.md", "targeted-bug-hunt.md", "security-audit.md",
        "architecture-audit.md", "performance-audit.md", "dependency-audit.md",
        "ci-audit.md", "testing-audit.md", "documentation-audit.md",
        "remediation-run.md", "verification-run.md", "regression-analysis.md",
        "pr-review.md", "incident-response.md", "debug-error.md",
        "trace-regression.md", "handoff-generation.md",
        "runtime-initialization.md", "artifact-generation.md",
        "evidence-capture.md", "final-quality-gate.md"
    ]
    for wf in expected_workflows:
        p = WORKFLOWS_DIR / wf
        assert p.is_file(), f"Missing workflow file: {wf}"
        content = p.read_text(encoding="utf-8")
        assert len(content.strip()) > 20, f"Workflow {wf} is too short or empty"


def test_workflow_objective_sections():
    for p in WORKFLOWS_DIR.glob("*.md"):
        content = p.read_text(encoding="utf-8")
        assert ("Objective" in content or "Phase" in content or "Workflow" in content), f"{p.name} missing objective or phase structure"
