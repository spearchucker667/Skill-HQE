import sys
from pathlib import Path
import tempfile
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from inventory_repo import classify_file, inventory_repository


def test_classify_file_categories():
    assert classify_file(Path("src/main.rs")) == "source"
    assert classify_file(Path("package.json")) == "config"
    assert classify_file(Path("tests/test_app.py")) == "test"
    assert classify_file(Path("docs/README.md")) == "docs"
    assert classify_file(Path("build/bundle.js")) == "build"
    assert classify_file(Path("target/debug/app.exe")) == "binary"
    assert classify_file(Path("assets/logo.png")) == "media"
    assert classify_file(Path("bundle.tar.gz")) == "archive"


def test_inventory_repository_counts():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        (root / "src").mkdir()
        (root / "src" / "main.py").write_text("print('hello')", encoding="utf-8")
        (root / "README.md").write_text("# Test", encoding="utf-8")
        (root / "test_main.py").write_text("def test_ok(): pass", encoding="utf-8")
        (root / ".gitignore").write_text("*.tmp\n", encoding="utf-8")
        (root / "cache.tmp").write_text("temp", encoding="utf-8")

        res = inventory_repository(root)
        assert res["total_files"] == 5
        assert res["excluded_files"] >= 1  # cache.tmp
        assert res["reviewable_files"] >= 3
        assert "categories" in res
        assert res["categories"]["source"] >= 1
        assert res["categories"]["docs"] >= 1
        assert res["categories"]["test"] >= 1
