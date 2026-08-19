"""Disk-verification tests for EvidenceStore evidence authenticity."""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from runtime import EvidenceStore, CodeEvidence


def test_matching_snippet_accepted():
    with tempfile.TemporaryDirectory() as tmpdir:
        src = Path(tmpdir) / "src.py"
        src.write_text("def hello():\n    return 42\n", encoding="utf-8")
        store = EvidenceStore(repo_root=tmpdir)
        ev = store.add_evidence(
            path="src.py",
            snippet="def hello():",
            start_line=1,
            end_line=1,
            verify_against_disk=True
        )
        assert ev.verified is True
        assert ev.verification_method == "line_range"


def test_fabricated_snippet_rejected():
    with tempfile.TemporaryDirectory() as tmpdir:
        src = Path(tmpdir) / "src.py"
        src.write_text("def hello():\n    return 42\n", encoding="utf-8")
        store = EvidenceStore(repo_root=tmpdir)
        with pytest.raises(ValueError, match="does not match disk content"):
            store.add_evidence(
                path="src.py",
                snippet="def goodbye():",
                start_line=1,
                end_line=1,
                verify_against_disk=True
            )


def test_out_of_range_line_rejected():
    with tempfile.TemporaryDirectory() as tmpdir:
        src = Path(tmpdir) / "src.py"
        src.write_text("def hello():\n    return 42\n", encoding="utf-8")
        store = EvidenceStore(repo_root=tmpdir)
        with pytest.raises(ValueError, match="exceeds file length"):
            store.add_evidence(
                path="src.py",
                snippet="def hello():",
                start_line=1,
                end_line=99,
                verify_against_disk=True
            )


def test_nonexistent_file_rejected():
    with tempfile.TemporaryDirectory() as tmpdir:
        store = EvidenceStore(repo_root=tmpdir)
        with pytest.raises(ValueError, match="does not exist"):
            store.add_evidence(
                path="missing.py",
                snippet="def hello():",
                start_line=1,
                end_line=1,
                verify_against_disk=True
            )


def test_path_escape_rejected():
    with tempfile.TemporaryDirectory() as tmpdir:
        store = EvidenceStore(repo_root=tmpdir)
        with pytest.raises(ValueError, match="Path traversal detected|outside repository"):
            store.add_evidence(
                path="../etc/passwd",
                snippet="root:",
                start_line=1,
                end_line=1,
                verify_against_disk=True
            )


def test_anchor_verification_accepted():
    with tempfile.TemporaryDirectory() as tmpdir:
        src = Path(tmpdir) / "src.py"
        src.write_text("class Greeter:\n    def hello(self):\n        pass\n", encoding="utf-8")
        store = EvidenceStore(repo_root=tmpdir)
        ev = store.add_evidence(
            path="src.py",
            snippet="class Greeter",
            anchor="class Greeter",
            verify_against_disk=True
        )
        assert ev.verified is True
        assert ev.verification_method == "anchor"


def test_ambiguous_anchor_rejected_when_uniqueness_required():
    with tempfile.TemporaryDirectory() as tmpdir:
        src = Path(tmpdir) / "src.py"
        src.write_text("def helper():\n    pass\n\ndef helper():\n    pass\n", encoding="utf-8")
        store = EvidenceStore(repo_root=tmpdir)
        with pytest.raises(ValueError, match="ambiguous anchor"):
            store.add_evidence(
                path="src.py",
                snippet="def helper():",
                anchor="def helper():",
                require_unique_anchor=True,
                verify_against_disk=True
            )


def test_no_locator_rejected_when_verification_enabled():
    with tempfile.TemporaryDirectory() as tmpdir:
        src = Path(tmpdir) / "src.py"
        src.write_text("def hello():\n    pass\n", encoding="utf-8")
        store = EvidenceStore(repo_root=tmpdir)
        with pytest.raises(ValueError, match="evidence locator"):
            store.add_evidence(
                path="src.py",
                snippet="def hello():",
                verify_against_disk=True
            )


def test_multi_line_snippet_with_anchor_accepted():
    """HQE evidence snippets are 2-5 lines; anchor verification must not assume a single line."""
    with tempfile.TemporaryDirectory() as tmpdir:
        src = Path(tmpdir) / "src.py"
        src.write_text(
            "def authenticate():\n"
            "    token = request.headers.get('Authorization')\n"
            "    return verify(token)\n",
            encoding="utf-8",
        )
        store = EvidenceStore(repo_root=tmpdir)
        ev = store.add_evidence(
            path="src.py",
            snippet="def authenticate():\n    token = request.headers.get('Authorization')\n    return verify(token)",
            anchor="def authenticate():",
            verify_against_disk=True
        )
        assert ev.verified is True
        assert ev.verification_method == "anchor"


def test_fabricated_snippet_with_genuine_anchor_rejected():
    """A fabricated snippet must fail even when the anchor itself exists in the file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        src = Path(tmpdir) / "src.py"
        src.write_text("class Greeter:\n    def hello(self):\n        pass\n", encoding="utf-8")
        store = EvidenceStore(repo_root=tmpdir)
        with pytest.raises(ValueError, match="snippet does not match disk content"):
            store.add_evidence(
                path="src.py",
                snippet="class Greeter:\n    return 'forged'",
                anchor="class Greeter",
                verify_against_disk=True
            )


def test_symbol_locator_checks_snippet_against_disk():
    with tempfile.TemporaryDirectory() as tmpdir:
        src = Path(tmpdir) / "src.py"
        src.write_text("def helper():\n    return 42\n", encoding="utf-8")
        store = EvidenceStore(repo_root=tmpdir)
        ev = store.add_evidence(
            path="src.py",
            snippet="def helper():\n    return 42",
            symbol="helper",
            verify_against_disk=True
        )
        assert ev.verified is True
        assert ev.verification_method == "symbol"


def test_code_evidence_validate_rejects_empty_snippet():
    ev = CodeEvidence(path="src.py", snippet="")
    assert any("snippet" in err for err in ev.validate())


def test_code_evidence_validate_rejects_invalid_line_range():
    ev = CodeEvidence(path="src.py", snippet="x", start_line=0, end_line=1)
    assert any("start_line" in err for err in ev.validate())


def test_code_evidence_validate_rejects_end_line_before_start():
    ev = CodeEvidence(path="src.py", snippet="x", start_line=5, end_line=2)
    assert any("end_line" in err for err in ev.validate())


def test_code_evidence_validate_rejects_incomplete_anchor_locator():
    ev = CodeEvidence(path="src.py", snippet="x", anchor="foo")
    assert any("anchor" in err and "grep_signature" in err for err in ev.validate())


def test_symbol_locator_rejects_fabricated_snippet():
    with tempfile.TemporaryDirectory() as tmpdir:
        src = Path(tmpdir) / "src.py"
        src.write_text("def helper():\n    return 42\n", encoding="utf-8")
        store = EvidenceStore(repo_root=tmpdir)
        with pytest.raises(ValueError, match="snippet does not match disk content"):
            store.add_evidence(
                path="src.py",
                snippet="def helper():\n    return 'forged'",
                symbol="helper",
                verify_against_disk=True
            )
