"""Tests for release-package minimality and macOS debris exclusion."""

import sys
import tempfile
import zipfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from package_skill import package_skill, should_exclude


def test_macos_metadata_is_excluded_by_should_exclude():
    assert should_exclude(".DS_Store")
    assert should_exclude("__MACOSX/hidden")
    assert should_exclude("dir/.DS_Store")


def test_development_and_test_directories_are_excluded():
    assert should_exclude("development/notes.md")
    assert should_exclude("archive/old.md")
    assert should_exclude("tests/test_foo.py")
    assert should_exclude("audit-output/report.md")


def test_cache_and_log_files_are_excluded():
    assert should_exclude("foo.pyc")
    assert should_exclude("__pycache__/module.cpython-311.pyc")
    assert should_exclude("debug.log")
    assert should_exclude("nested.zip")


def test_real_release_excludes_macos_debris_and_dev_dirs():
    with tempfile.TemporaryDirectory() as tmpdir:
        out = Path(tmpdir) / "skill.zip"
        result = package_skill(ROOT, out)
        assert result["clean_verification"] is True

        with zipfile.ZipFile(out, "r") as zf:
            names = zf.namelist()

        lower_names = [n.lower() for n in names]
        assert not any(".ds_store" in n for n in lower_names)
        assert not any("__macosx" in n for n in lower_names)
        assert not any("tests/" in n for n in names)
        assert not any("development/" in n for n in names)
        assert not any("archive/" in n for n in names)
        assert not any(n.endswith(".pyc") for n in names)
        assert not any("__pycache__" in n for n in names)


def test_release_contains_required_skill_files():
    with tempfile.TemporaryDirectory() as tmpdir:
        out = Path(tmpdir) / "skill.zip"
        package_skill(ROOT, out)

        with zipfile.ZipFile(out, "r") as zf:
            names = zf.namelist()

        assert any("SKILL.md" in n for n in names)
        assert any("runtime/__init__.py" in n for n in names)
        assert any("protocol/hqe-engineer.yaml" in n for n in names)


def test_release_excludes_optional_tooling_configs():
    with tempfile.TemporaryDirectory() as tmpdir:
        out = Path(tmpdir) / "skill.zip"
        package_skill(ROOT, out)

        with zipfile.ZipFile(out, "r") as zf:
            names = zf.namelist()

        assert not any(n.endswith(".actionlint.yaml") for n in names)
        assert not any(n.endswith(".pre-commit-config.yaml") for n in names)
