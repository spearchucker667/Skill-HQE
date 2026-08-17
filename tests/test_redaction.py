import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from redact_secrets import redact_text, redact_findings_file


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
