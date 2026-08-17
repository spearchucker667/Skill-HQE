"""Redaction tests covering runtime engine, scripts wrapper, and fail-closed behavior."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from runtime import TypedRedactionEngine, classify_secret
from runtime.redaction_engine import redact_text
from redact_secrets import redact_text as script_redact_text


def test_redact_aws_key():
    text = "Deploying with AKIA1234567890ABCDEF key"
    redacted, count = redact_text(text)
    assert "AKIA" not in redacted
    assert "REDACTED_AWS_ACCESS_KEY" in redacted
    assert count == 1


def test_redact_github_token():
    text = "Token: ghp_123456789012345678901234567890123456"
    redacted, count = redact_text(text)
    assert "ghp_" not in redacted
    assert "REDACTED_GITHUB_TOKEN" in redacted
    assert count == 1


def test_redact_slack_token():
    text = "xoxb-1234567890-123456789012"
    redacted, count = redact_text(text)
    assert "xoxb-" not in redacted
    assert "REDACTED_SLACK_TOKEN" in redacted
    assert count == 1


def test_typed_engine_records_categories():
    engine = TypedRedactionEngine()
    redacted = engine.redact("key=AKIA1234567890ABCDEF token=xoxb-1234567890-123456789012")
    assert "AKIA" not in redacted
    assert "xoxb-" not in redacted
    summary = engine.typed_summary()
    assert summary["total_redactions"] == 2
    categories = {e["category"] for e in summary["typed_entries"]}
    assert "api_key" in categories
    assert "token" in categories


def test_classify_secret_categories():
    assert classify_secret("AKIA1234567890ABCDEF") == "api_key"
    assert classify_secret("xoxb-1234567890-123456789012") == "token"
    assert classify_secret("postgres://user:pass@host/db") == "database_url"


def test_script_wrapper_uses_runtime_engine():
    """The CLI wrapper must produce the same redacted output as the runtime engine."""
    text = "key=AKIA1234567890ABCDEF"
    runtime_redacted, runtime_count = redact_text(text)
    script_redacted, script_count = script_redact_text(text)
    assert runtime_redacted == script_redacted
    assert runtime_count == script_count


def test_evidence_store_does_not_return_raw_secrets_on_redaction_failure(monkeypatch):
    from runtime import EvidenceStore

    def broken_redact(_txt: str) -> tuple[str, int]:
        raise RuntimeError("redactor unavailable")

    monkeypatch.setattr("runtime.evidence_store.redact_text", broken_redact)
    store = EvidenceStore()
    with pytest.raises(RuntimeError, match="redactor unavailable"):
        store.add_evidence(path="x.py", snippet="AKIA1234567890ABCDEF")


def test_record_tool_execution_redacts_on_failure(monkeypatch):
    from runtime import EvidenceStore

    def broken_redact(_txt: str) -> tuple[str, int]:
        raise RuntimeError("redactor unavailable")

    monkeypatch.setattr("runtime.evidence_store.redact_text", broken_redact)
    store = EvidenceStore()
    with pytest.raises(RuntimeError, match="redactor unavailable"):
        store.record_tool_execution("pytest", "pytest", 0, stdout="xoxb-1234567890-123456789012")
