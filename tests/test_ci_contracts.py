"""CI workflow contract tests for Skill-HQE."""

from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"


def _load_workflow(name: str) -> str:
    return (WORKFLOWS / name).read_text(encoding="utf-8")


def test_validate_skill_uses_requirements_dev_not_editable_install():
    """Editable installs fail on flat-layout content repositories."""
    content = _load_workflow("validate-skill.yml")
    assert 'pip install -e ".[dev]"' not in content
    assert "pip install -r requirements-dev.txt" in content


def test_validate_skill_sets_python_dont_write_bytecode():
    content = _load_workflow("validate-skill.yml")
    assert "PYTHONDONTWRITEBYTECODE" in content


def test_validate_skill_triggers_on_runtime_protocol_and_requirements():
    content = _load_workflow("validate-skill.yml")
    assert "- 'runtime/**'" in content
    assert "- 'protocol/**'" in content
    assert "- 'requirements-dev.txt'" in content


def test_ci_and_validate_skill_use_same_dependency_source():
    ci = _load_workflow("ci.yml")
    validate = _load_workflow("validate-skill.yml")
    assert "pip install -r requirements-dev.txt" in ci
    assert "pip install -r requirements-dev.txt" in validate


def test_no_editable_install_in_any_workflow():
    for wf in WORKFLOWS.glob("*.yml"):
        content = wf.read_text(encoding="utf-8")
        assert "pip install -e" not in content, f"Editable install found in {wf.name}"
