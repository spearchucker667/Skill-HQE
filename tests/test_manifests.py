import sys
from pathlib import Path
import tempfile
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from detect_manifests import detect_manifests


def test_detect_manifests_polyglot():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        (root / "Cargo.toml").write_text("[package]\nname = 'test'\n", encoding="utf-8")
        (root / "package.json").write_text('{"name": "test"}', encoding="utf-8")
        (root / "pyproject.toml").write_text("[project]\nname = 'test'\n", encoding="utf-8")
        (root / "go.mod").write_text("module test\n", encoding="utf-8")

        res = detect_manifests(root)
        assert res["total_matches"] == 4
        assert res["returned_matches"] == 4
        assert not res["truncated"]
        assert "rust" in res["ecosystems_detected"]
        assert "node" in res["ecosystems_detected"]
        assert "python" in res["ecosystems_detected"]
        assert "go" in res["ecosystems_detected"]


def test_detect_manifests_truncation_flag():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        for i in range(10):
            sub = root / f"pkg_{i}"
            sub.mkdir()
            (sub / "package.json").write_text('{"name": "test"}', encoding="utf-8")

        res = detect_manifests(root, max_results=5)
        assert res["total_matches"] == 10
        assert res["returned_matches"] == 5
        assert res["truncated"] is True
