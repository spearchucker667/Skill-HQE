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

# Detection vectors are assembled at runtime from nonmatching fragments so the
# repository itself never contains literal credential patterns. This keeps the
# scanner test coverage intact while avoiding false positives in repository-wide
# secret scanning (ours and GitHub's).
AWS_KEY = "AKIA" + "1234567890ABCDEF"
SLACK_TOKEN = "xox" + "b-1234567890-123456789012"
GITHUB_TOKEN = "ghp_" + "123456789012345678901234567890123456"


def test_redact_aws_key():
    text = "Deploying with " + AWS_KEY + " key"
    redacted, count = redact_text(text)
    assert "AKIA" not in redacted
    assert "REDACTED_AWS_ACCESS_KEY" in redacted
    assert count == 1


def test_redact_github_token():
    text = "Token: " + GITHUB_TOKEN
    redacted, count = redact_text(text)
    assert "ghp_" not in redacted
    assert "REDACTED_GITHUB_TOKEN" in redacted
    assert count == 1


def test_redact_slack_token():
    text = SLACK_TOKEN
    redacted, count = redact_text(text)
    assert "xoxb-" not in redacted
    assert "REDACTED_SLACK_TOKEN" in redacted
    assert count == 1


def test_typed_engine_records_categories():
    engine = TypedRedactionEngine()
    redacted = engine.redact("key=" + AWS_KEY + " token=" + SLACK_TOKEN)
    assert "AKIA" not in redacted
    assert "xoxb-" not in redacted
    summary = engine.typed_summary()
    assert summary["total_redactions"] == 2
    categories = {e["category"] for e in summary["typed_entries"]}
    assert "api_key" in categories
    assert "token" in categories


def test_classify_secret_categories():
    assert classify_secret(AWS_KEY) == "api_key"
    assert classify_secret(SLACK_TOKEN) == "token"
    assert classify_secret("postgres://user:pass@host/db") == "database_url"


def test_script_wrapper_uses_runtime_engine():
    """The CLI wrapper must produce the same redacted output as the runtime engine."""
    text = "key=" + AWS_KEY
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
        store.add_evidence(path="x.py", snippet=AWS_KEY)


def test_record_tool_execution_redacts_on_failure(monkeypatch):
    from runtime import EvidenceStore

    def broken_redact(_txt: str) -> tuple[str, int]:
        raise RuntimeError("redactor unavailable")

    monkeypatch.setattr("runtime.evidence_store.redact_text", broken_redact)
    store = EvidenceStore()
    with pytest.raises(RuntimeError, match="redactor unavailable"):
        store.record_tool_execution("pytest", "pytest", 0, stdout=SLACK_TOKEN)
