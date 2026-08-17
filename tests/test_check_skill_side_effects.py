"""Tests that check_skill.py does not leave bytecode or other side effects."""

import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def test_check_skill_does_not_create_pycache():
    with tempfile.TemporaryDirectory() as tmpdir:
        # Copy a minimal subset to a temp tree so we can observe side effects.
        temp_root = Path(tmpdir) / "skill"
        temp_root.mkdir()
        # Copy required runtime files (with at least one .py to compile).
        (temp_root / "runtime").mkdir()
        (temp_root / "runtime" / "__init__.py").write_text("# ok\n", encoding="utf-8")
        (temp_root / "SKILL.md").write_text(
            "Phase -1\nPhase 0\nprotocol/hqe-engineer.yaml\n5.0.0\n"
            "NEEDS_VERIFICATION\nZero Hallucination\nMandatory Evidence\n"
            "No Secret Leakage\nMinimal Change\nHealth Scoring\nSeverity Gates\n"
            "Taint Chains\nChange Budget\nStop-the-Line\nPre-Delivery\n",
            encoding="utf-8",
        )
        for fname in ["README.md", "LICENSE", "NOTICE", "VERSION", "CHANGELOG.md",
                      "CONTRIBUTING.md", "SECURITY.md", "CODE_OF_CONDUCT.md",
                      "PRIVACY.md", "TERMS_OF_SERVICE.md", "pyproject.toml",
                      "requirements-dev.txt"]:
            (temp_root / fname).write_text("# placeholder\n", encoding="utf-8")

        before = list(temp_root.rglob("__pycache__"))
        subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "check_skill.py"), str(temp_root)],
            capture_output=True,
            text=True,
        )
        after = list(temp_root.rglob("__pycache__"))

        assert before == after, "check_skill.py created __pycache__ in the target tree"
