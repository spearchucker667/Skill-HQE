import sys
from pathlib import Path
import tempfile
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from local_risk_scan import scan_local_risks

# Runtime-constructed detection vector (see tests/test_redaction.py).
AWS_KEY = "AKIA" + "1234567890ABCDEF"


def test_scan_ungitignored_env():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        (root / ".env").write_text("DATABASE_URL=postgres://...\n", encoding="utf-8")
        findings = scan_local_risks(root)
        types = [f["finding_type"] for f in findings]
        assert "UNGITIGNORED_ENV" in types


def test_scan_hardcoded_secret():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        (root / ".gitignore").write_text(".env\n", encoding="utf-8")
        (root / "src").mkdir()
        (root / "src" / "client.py").write_text('API_KEY = "' + AWS_KEY + '"\n', encoding="utf-8")
        findings = scan_local_risks(root)
        types = [f["finding_type"] for f in findings]
        assert any("AWS_KEY" in t or "SECRET" in t for t in types)


def test_scan_sql_injection_risk():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        (root / ".gitignore").write_text(".env\n", encoding="utf-8")
        (root / "src").mkdir()
        (root / "src" / "db.py").write_text('query = "SELECT * FROM users WHERE id = %s" % user_id\n', encoding="utf-8")
        findings = scan_local_risks(root)
        types = [f["finding_type"] for f in findings]
        assert "SQL_INJECTION_RISK" in types
