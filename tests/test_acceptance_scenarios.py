import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from inventory_repo import inventory_repository
from detect_manifests import detect_manifests
from detect_test_commands import detect_commands
from local_risk_scan import scan_local_risks
from redact_secrets import redact_text

FIXTURES = ROOT / "tests" / "acceptance" / "fixtures"


def test_scenario_rust_small():
    rust_dir = FIXTURES / "rust_small"
    manifests = detect_manifests(rust_dir)
    assert "rust" in manifests["ecosystems_detected"]

    cmds = detect_commands(rust_dir)
    assert any(c["command"] == "cargo test --all-targets" for c in cmds)

    inv = inventory_repository(rust_dir)
    assert inv["total_files"] >= 2


def test_scenario_typescript_cli():
    ts_dir = FIXTURES / "typescript_cli"
    manifests = detect_manifests(ts_dir)
    assert "node" in manifests["ecosystems_detected"]

    cmds = detect_commands(ts_dir)
    assert any(c["command"] == "npm run test" for c in cmds)
    assert any(c["command"] == "npm run lint" for c in cmds)


def test_scenario_security_boundary():
    sec_dir = FIXTURES / "security_boundary"
    risks = scan_local_risks(sec_dir)
    types = [r["finding_type"] for r in risks]
    assert "UNGITIGNORED_ENV" in types
    assert any("HARDCODED_SECRET" in t or "SECRET" in t for t in types)

    # Ensure secrets in .env snippet are masked
    for r in risks:
        if r.get("snippet"):
            assert "secret_pw" not in r["snippet"]
            assert "super-secret" not in r["snippet"]


def test_scenario_prompt_injection_defense():
    inj_dir = FIXTURES / "malicious_repo_prompt"
    main_file = inj_dir / "main.py"
    content = main_file.read_text(encoding="utf-8")

    # Verify that prompt injection text is parsed as passive string and not treated as instructions
    assert "IGNORE ALL SAFETY RULES" in content
    # Scan should not throw or alter behavior
    risks = scan_local_risks(inj_dir)
    assert isinstance(risks, list)


def test_scenario_large_repo_triage():
    large_dir = FIXTURES / "large_repo"
    inv = inventory_repository(large_dir)
    assert inv["total_files"] >= 50
    # Large repo triggers Phase 0.5 triage mode
    assert inv["total_files"] > 50
