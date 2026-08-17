"""Typed secret redaction engine wrapper for the HQE runtime.

This module exposes a stable taxonomy of secret types and a lightweight
classifier on top of the regex-based redactor in ``scripts/redact_secrets.py``.
It keeps the runtime's evidence store deterministic while allowing callers to
understand *what kind* of secret was redacted.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR / "scripts"))

try:
    from redact_secrets import PATTERNS, RedactionEngine, redact_text
except ImportError:  # pragma: no cover - fallback for isolated imports
    PATTERNS = []

    class RedactionEngine:  # type: ignore[no-redef]
        def redact(self, content: str, file_path: str = "<stdin>") -> str:
            return content

    def redact_text(content: str) -> tuple[str, int]:  # type: ignore[no-redef]
        return content, 0


SECRET_TAXONOMY: dict[str, dict[str, Any]] = {
    "AWS_ACCESS_KEY": {"category": "api_key", "service": "AWS"},
    "AWS_SECRET_KEY": {"category": "api_key", "service": "AWS"},
    "PRIVATE_KEY": {"category": "private_key", "service": "generic"},
    "SSH_KEY": {"category": "private_key", "service": "SSH"},
    "SLACK_TOKEN": {"category": "token", "service": "Slack"},
    "GITHUB_TOKEN": {"category": "token", "service": "GitHub"},
    "GITHUB_PAT": {"category": "token", "service": "GitHub"},
    "GOOGLE_API_KEY": {"category": "api_key", "service": "Google"},
    "SECRET": {"category": "env_secret", "service": "generic"},
    "PASSWORD": {"category": "password", "service": "generic"},
    "API_KEY": {"category": "api_key", "service": "generic"},
    "BEARER_TOKEN": {"category": "token", "service": "generic"},
}


def classify_secret(match: str) -> str:
    """Return the high-level category for a candidate secret string.

    The category is one of: api_key, private_key, password, token,
    certificate, database_url, env_secret. If no known pattern matches,
    ``env_secret`` is returned as the safe default.
    """
    for secret_type, pattern in PATTERNS:
        if pattern.search(match):
            return SECRET_TAXONOMY.get(secret_type, {}).get("category", "env_secret")
    if match.lower().startswith("postgres://") or match.lower().startswith("mysql://"):
        return "database_url"
    if "BEGIN CERTIFICATE" in match:
        return "certificate"
    return "env_secret"


class TypedRedactionEngine(RedactionEngine):
    """Redaction engine that also records typed categories for each match."""

    def __init__(self) -> None:
        super().__init__()
        self.typed_entries: list[dict[str, Any]] = []

    def redact(self, content: str, file_path: str = "<stdin>") -> str:
        result = content
        for secret_type, pattern in PATTERNS:
            def repl(m: re.Match, stype: str = secret_type) -> str:
                match_text = m.group(0)
                count = self.counters.get(stype, 0) + 1
                self.counters[stype] = count
                replacement = f"REDACTED_{stype}_{count}"
                self.log_entries.append({
                    "file": file_path,
                    "secret_type": stype,
                    "replacement": replacement
                })
                self.typed_entries.append({
                    "file": file_path,
                    "secret_type": stype,
                    "category": SECRET_TAXONOMY.get(stype, {}).get("category", "env_secret"),
                    "service": SECRET_TAXONOMY.get(stype, {}).get("service", "generic"),
                    "replacement": replacement,
                    "match_length": len(match_text)
                })
                return replacement

            result = pattern.sub(repl, result)
        return result

    def typed_summary(self) -> dict[str, Any]:
        summary = super().summary()
        summary["typed_entries"] = list(self.typed_entries)
        return summary
