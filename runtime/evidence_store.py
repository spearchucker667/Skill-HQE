"""Evidence collection, verification, and tool execution tracking for HQE."""

from __future__ import annotations

import datetime
import hashlib
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .redaction_engine import redact_text


def _normalize_line(text: str) -> str:
    """Normalize line content for snippet comparison.

    Strips leading/trailing whitespace and collapses internal whitespace
    sequences so minor formatting differences do not break verification.
    """
    return " ".join(text.strip().split())


@dataclass
class CodeEvidence:
    path: str
    snippet: str
    start_line: int | None = None
    end_line: int | None = None
    symbol: str | None = None
    anchor: str | None = None
    grep_signature: str | None = None
    verified: bool = False
    verification_method: str | None = None
    verified_at: str | None = None
    source_hash: str | None = None

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "path": self.path,
            "snippet": self.snippet
        }
        if self.start_line is not None:
            data["start_line"] = self.start_line
        if self.end_line is not None:
            data["end_line"] = self.end_line
        if self.symbol is not None:
            data["symbol"] = self.symbol
        if self.anchor is not None:
            data["anchor"] = self.anchor
        if self.grep_signature is not None:
            data["grep_signature"] = self.grep_signature
        if self.verified:
            data["verified"] = self.verified
        if self.verification_method is not None:
            data["verification_method"] = self.verification_method
        if self.verified_at is not None:
            data["verified_at"] = self.verified_at
        if self.source_hash is not None:
            data["source_hash"] = self.source_hash
        return data


class EvidenceStore:
    def __init__(self, repo_root: Path | str = "."):
        self.repo_root = Path(repo_root).resolve()
        self.evidence_items: list[CodeEvidence] = []
        self.tool_executions: list[dict[str, Any]] = []

    def _safe_resolve(self, path: str) -> Path:
        """Resolve a repo-relative path, rejecting traversal outside repo_root."""
        raw = self.repo_root / path
        if ".." in raw.parts:
            raise ValueError(f"Path traversal detected: {path}")
        try:
            resolved = raw.resolve()
            resolved.relative_to(self.repo_root)
        except ValueError as exc:
            raise ValueError(f"Evidence path outside repository: {path}") from exc
        return resolved

    def _verify_line_range(
        self,
        target_path: Path,
        snippet: str,
        start_line: int | None,
        end_line: int | None
    ) -> tuple[bool, str | None]:
        """Return (verified, method_or_error)."""
        if start_line is None or end_line is None:
            return False, "line range verification requires start_line and end_line"

        file_text = target_path.read_text(encoding="utf-8", errors="replace")
        lines = file_text.splitlines()

        if end_line > len(lines):
            return False, f"end_line ({end_line}) exceeds file length ({len(lines)})"

        selected = "\n".join(lines[start_line - 1:end_line])
        expected = _normalize_line(snippet)
        actual = _normalize_line(selected)
        if expected != actual:
            return False, "snippet does not match disk content for claimed line range"
        return True, "line_range"

    def _verify_anchor(
        self,
        target_path: Path,
        snippet: str,
        anchor: str,
        require_unique: bool
    ) -> tuple[bool, str | None]:
        """Return (verified, method_or_error)."""
        file_text = target_path.read_text(encoding="utf-8", errors="replace")
        lines = file_text.splitlines()
        matches = [idx for idx, line in enumerate(lines, start=1) if anchor in line]

        if not matches:
            return False, f"anchor not found in {target_path.name}"

        if require_unique and len(matches) > 1:
            return False, f"ambiguous anchor: {len(matches)} occurrences in {target_path.name}"

        # Also require the snippet content to appear at one of the anchor lines.
        normalized_snippet = _normalize_line(snippet)
        for line_no in matches:
            if normalized_snippet in _normalize_line(lines[line_no - 1]):
                return True, "anchor"
        return False, "snippet not found near anchor"

    def add_evidence(
        self,
        path: str,
        snippet: str,
        start_line: int | None = None,
        end_line: int | None = None,
        symbol: str | None = None,
        anchor: str | None = None,
        grep_signature: str | None = None,
        verify_against_disk: bool = False,
        require_unique_anchor: bool = False
    ) -> CodeEvidence:
        """Add and validate code evidence triad.

        When ``verify_against_disk`` is True, the evidence must carry a valid
        locator (line range or anchor) and the submitted snippet must match the
        actual file content. Path traversal outside ``repo_root`` is rejected.
        """
        clean_snippet, _ = redact_text(snippet.strip())
        if not clean_snippet:
            raise ValueError("Snippet cannot be empty")

        if start_line is not None:
            if start_line < 1:
                raise ValueError(f"start_line must be >= 1 (got {start_line})")
            if end_line is not None and end_line < start_line:
                raise ValueError(f"end_line ({end_line}) cannot be less than start_line ({start_line})")

        verified = False
        verification_method = None
        source_hash = None

        if verify_against_disk:
            target_path = self._safe_resolve(path)
            if not target_path.is_file():
                raise ValueError(f"Evidence file does not exist: {path}")

            has_line_range = start_line is not None and end_line is not None
            has_anchor = anchor is not None

            if not has_line_range and not has_anchor and not symbol and not grep_signature:
                raise ValueError(
                    "Disk verification requires an evidence locator (line range, anchor, symbol, or grep_signature)"
                )

            file_bytes = target_path.read_bytes()
            source_hash = hashlib.sha256(file_bytes).hexdigest()

            if has_line_range:
                ok, result = self._verify_line_range(target_path, clean_snippet, start_line, end_line)
                if not ok:
                    raise ValueError(result)
                verified = True
                verification_method = result
            elif has_anchor:
                ok, result = self._verify_anchor(
                    target_path, clean_snippet, anchor, require_unique_anchor
                )
                if not ok:
                    raise ValueError(result)
                verified = True
                verification_method = result
            else:
                # symbol/grep_signature locators are accepted but cannot be
                # cryptographically verified from disk alone; record them as
                # unverified disk checks.
                verification_method = "locator_present"

        item = CodeEvidence(
            path=path,
            snippet=clean_snippet,
            start_line=start_line,
            end_line=end_line,
            symbol=symbol,
            anchor=anchor,
            grep_signature=grep_signature,
            verified=verified,
            verification_method=verification_method,
            verified_at=datetime.datetime.now(datetime.timezone.utc).isoformat() if verified else None,
            source_hash=source_hash
        )
        self.evidence_items.append(item)
        return item

    def record_tool_execution(
        self,
        tool_name: str,
        command: str,
        exit_code: int,
        stdout: str = "",
        stderr: str = "",
        executed: bool = True
    ) -> dict[str, Any]:
        """Record tool invocation with automatic secret redaction."""
        redacted_cmd, _ = redact_text(command)
        redacted_out, _ = redact_text(stdout)
        redacted_err, _ = redact_text(stderr)
        record = {
            "tool_name": tool_name,
            "command": redacted_cmd,
            "exit_code": exit_code,
            "stdout": redacted_out,
            "stderr": redacted_err,
            "executed": executed
        }
        self.tool_executions.append(record)
        return record

    def get_summary(self) -> dict[str, Any]:
        return {
            "total_evidence_items": len(self.evidence_items),
            "total_tools_executed": len(self.tool_executions),
            "tools_used": sorted(list({t["tool_name"] for t in self.tool_executions}))
        }
