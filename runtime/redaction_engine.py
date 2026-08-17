"""Canonical secret redaction engine for the HQE runtime.

This module is the single source of truth for secret detection and redaction.
The CLI wrapper in ``scripts/redact_secrets.py`` imports from here so that
runtime evidence processing and command-line redaction behave identically.
"""

from __future__ import annotations

import re
from typing import Any

# Negative lookahead to avoid re-redacting our own replacement tokens.
_NO_REDACTED = r"(?!REDACTED_)"

PATTERNS = [
    ("AWS_ACCESS_KEY", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("AWS_SECRET_KEY", re.compile(r"\b[0-9a-zA-Z/+]{40}\b")),
    ("SSH_KEY", re.compile(r"-----BEGIN OPENSSH PRIVATE KEY-----[\s\S]*?-----END OPENSSH PRIVATE KEY-----")),
    ("PRIVATE_KEY", re.compile(r"-----BEGIN (?:RSA |DSA |EC |OPENSSH |ENCRYPTED |PGP )?PRIVATE KEY(?: BLOCK)?-----[\s\S]*?-----END (?:RSA |DSA |EC |OPENSSH |ENCRYPTED |PGP )?PRIVATE KEY(?: BLOCK)?-----")),
    ("PRIVATE_KEY_HEADER", re.compile(r"-----BEGIN (?:RSA |DSA |EC |OPENSSH |ENCRYPTED |PGP )?PRIVATE KEY(?: BLOCK)?-----")),
    ("SLACK_TOKEN", re.compile(r"xox[baprs]-[0-9a-zA-Z-]+")),
    ("GITHUB_TOKEN", re.compile(r"gh[pousr]_[0-9a-zA-Z_]{36,}")),
    ("GITHUB_PAT", re.compile(r"github_pat_[0-9a-zA-Z_]+")),
    ("GOOGLE_API_KEY", re.compile(r"AIza[0-9A-Za-z_-]{35}")),
    ("OPENAI_API_KEY", re.compile(r"sk-[a-zA-Z0-9]{32,}")),
    ("SECRET", re.compile(rf'(?i)(secret|private[_-]?key)\s*[=:]\s*["\']?{_NO_REDACTED}[a-zA-Z0-9_-]{{8,64}}["\']?')),
    ("PASSWORD", re.compile(rf'(?i)(password|passwd|pwd)\s*[=:]\s*["\']{_NO_REDACTED}[^"\']{{8,128}}["\']')),
    ("API_KEY", re.compile(rf'(?i)api[_-]?key["\']?\s*[:=]\s*["\']{_NO_REDACTED}[a-zA-Z0-9_-]{{16,64}}["\']')),
    ("BEARER_TOKEN", re.compile(rf'(?i)bearer\s+{_NO_REDACTED}[a-zA-Z0-9_\-\.=]{{20,}}')),
    ("TOKEN", re.compile(rf'(?i)(token|auth[_-]?token)\s*[=:]\s*["\']?{_NO_REDACTED}[a-zA-Z0-9_-]{{10,64}}["\']?')),
]

SECRET_TAXONOMY: dict[str, dict[str, Any]] = {
    "AWS_ACCESS_KEY": {"category": "api_key", "service": "AWS"},
    "AWS_SECRET_KEY": {"category": "api_key", "service": "AWS"},
    "SSH_KEY": {"category": "private_key", "service": "SSH"},
    "PRIVATE_KEY": {"category": "private_key", "service": "generic"},
    "PRIVATE_KEY_HEADER": {"category": "private_key", "service": "generic"},
    "SLACK_TOKEN": {"category": "token", "service": "Slack"},
    "GITHUB_TOKEN": {"category": "token", "service": "GitHub"},
    "GITHUB_PAT": {"category": "token", "service": "GitHub"},
    "GOOGLE_API_KEY": {"category": "api_key", "service": "Google"},
    "OPENAI_API_KEY": {"category": "api_key", "service": "OpenAI"},
    "SECRET": {"category": "env_secret", "service": "generic"},
    "PASSWORD": {"category": "password", "service": "generic"},
    "API_KEY": {"category": "api_key", "service": "generic"},
    "BEARER_TOKEN": {"category": "token", "service": "generic"},
    "TOKEN": {"category": "token", "service": "generic"},
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


class RedactionEngine:
    """Regex-based secret redaction engine."""

    def __init__(self) -> None:
        self.counters: dict[str, int] = {}
        self.log_entries: list[dict[str, Any]] = []

    def redact(self, content: str, file_path: str = "<stdin>") -> str:
        result = content
        for secret_type, pattern in PATTERNS:
            def repl(m: re.Match, stype: str = secret_type) -> str:
                count = self.counters.get(stype, 0) + 1
                self.counters[stype] = count
                replacement = f"REDACTED_{stype}_{count}"
                self.log_entries.append({
                    "file": file_path,
                    "secret_type": stype,
                    "replacement": replacement
                })
                return replacement

            result = pattern.sub(repl, result)
        return result

    def summary(self) -> dict[str, Any]:
        total = sum(self.counters.values())
        return {
            "total_redactions": total,
            "by_type": dict(self.counters),
            "entries": list(self.log_entries)
        }

    def reset(self) -> None:
        self.counters.clear()
        self.log_entries.clear()


def redact_text(content: str) -> tuple[str, int]:
    """Convenience helper to redact a string and return (redacted_str, total_count)."""
    engine = RedactionEngine()
    redacted = engine.redact(content)
    return redacted, engine.summary()["total_redactions"]


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
