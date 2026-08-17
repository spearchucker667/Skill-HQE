import sys
from pathlib import Path
import tempfile
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from detect_test_commands import detect_commands


def test_detect_commands_node():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        (root / "package.json").write_text(
            '{"scripts": {"test:unit": "jest", "lint": "eslint .", "typecheck": "tsc"}}',
            encoding="utf-8"
        )
        cmds = detect_commands(root)
        kinds = {c["kind"]: c for c in cmds}
        assert "test" in kinds
        assert kinds["test"]["command"] == "npm run test:unit"
        assert kinds["test"]["executed"] is False
        assert "lint" in kinds
        assert "typecheck" in kinds


def test_detect_commands_rust():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        (root / "Cargo.toml").write_text('[package]\nname = "test"\n', encoding="utf-8")
        cmds = detect_commands(root)
        kinds = [c["kind"] for c in cmds]
        assert "test" in kinds
        assert "lint" in kinds
        assert "typecheck" in kinds
        assert "format-check" in kinds
        assert "build" in kinds
        for c in cmds:
            assert c["executed"] is False
