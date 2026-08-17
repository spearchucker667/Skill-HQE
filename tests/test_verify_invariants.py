"""Tests for scripts/verify_invariants.sh."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "verify_invariants.sh"


def test_verify_invariants_script_exists_and_is_executable():
    assert SCRIPT.is_file(), f"Missing script: {SCRIPT}"
    assert SCRIPT.stat().st_mode & 0o111, f"Script is not executable: {SCRIPT}"


def test_verify_invariants_runs_successfully():
    result = subprocess.run(
        ["bash", str(SCRIPT), str(ROOT)],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )
    assert result.returncode == 0, (
        f"verify_invariants.sh failed with exit code {result.returncode}\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "[verify_invariants] OK" in result.stdout
