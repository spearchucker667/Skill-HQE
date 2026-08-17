import sys
from pathlib import Path
import tempfile
import zipfile
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from package_skill import package_skill
from check_release_contents import check_zip_archive


def test_packaging_cleanliness():
    with tempfile.TemporaryDirectory() as tmpdir:
        out_zip = Path(tmpdir) / "test_skill.zip"
        res = package_skill(ROOT, out_zip)
        assert res["clean_verification"] is True
        assert out_zip.is_file()

        # Verify allowlist check
        errors = check_zip_archive(out_zip)
        assert not errors, f"Release check errors: {errors}"

        with zipfile.ZipFile(out_zip, "r") as zf:
            names = zf.namelist()
            for name in names:
                assert not name.startswith("__MACOSX")
                assert ".git/" not in name
                assert "__pycache__" not in name
                assert not name.endswith(".pyc")
                assert ".DS_Store" not in name
                assert "development/" not in name
                assert "archive/" not in name
                assert "tests/" not in name
                assert not name.endswith(".log")
                assert not name.endswith(".zip")

