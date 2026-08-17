"""Tests for the CI secret scanner."""

import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.scan_secrets import scan_directory, scan_file, main


def test_scan_file_detects_secret_without_leaking_it():
    with tempfile.TemporaryDirectory() as tmpdir:
        target = Path(tmpdir) / "config.py"
        target.write_text('api_key = "AKIA1234567890ABCDEF"\n', encoding="utf-8")
        matches = scan_file(target)
        assert len(matches) == 1
        line_no, secret_type = matches[0]
        assert line_no == 1
        assert secret_type == "AWS_ACCESS_KEY"
        # Raw secret must not be present in the match tuple.
        assert "AKIA" not in str(matches)


def test_scan_directory_respects_allowlist():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        real = root / "real_secret.py"
        fixture = root / "tests" / "fixture.py"
        fixture.parent.mkdir()
        real.write_text('key = "AKIA1234567890ABCDEF"\n', encoding="utf-8")
        fixture.write_text('key = "AKIA1234567890ABCDEF"\n', encoding="utf-8")

        without_allowlist = scan_directory(root)
        assert len(without_allowlist) == 2

        with_allowlist = scan_directory(root, allowlist=["tests/"])
        assert len(with_allowlist) == 1
        assert with_allowlist[0][0].name == "real_secret.py"


def test_scan_directory_skips_binary_files():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        binary = root / "image.png"
        binary.write_bytes(b"\x89PNG\r\n\x1a\n" + b"AKIA1234567890ABCDEF" * 10)
        matches = scan_directory(root)
        assert matches == []


def test_main_reports_findings_and_exits_nonzero():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        secret_file = root / "keys.py"
        secret_file.write_text('slack = "xoxb-1234567890-123456789012"\n', encoding="utf-8")

        code = main([str(root)])
        assert code == 1


def test_main_returns_zero_when_clean():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        clean = root / "readme.md"
        clean.write_text("# No secrets here\n", encoding="utf-8")

        code = main([str(root)])
        assert code == 0


def test_scanner_does_not_print_raw_secret():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        secret_file = root / "keys.py"
        secret_file.write_text('openai = "sk-abcdefghijklmnopqrstuvwxyz123456"\n', encoding="utf-8")

        import io
        captured = io.StringIO()
        # main prints to stdout; capture it.
        import scripts.scan_secrets as ss
        old_stdout = sys.stdout
        sys.stdout = captured
        try:
            main([str(root)])
        finally:
            sys.stdout = old_stdout
        output = captured.getvalue()
        assert "OPENAI_API_KEY" in output
        assert "sk-abcdefghijklmnopqrstuvwxyz123456" not in output
