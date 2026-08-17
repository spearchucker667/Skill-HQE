"""Evidence collection, verification, and tool execution tracking for HQE."""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# Use redact_secrets utility from scripts
ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR / "scripts"))
try:
    from redact_secrets import redact_text
except ImportError:
    def redact_text(txt: str) -> tuple[str, int]:
        return txt, 0


@dataclass
class CodeEvidence:
    path: str
    snippet: str
    start_line: int | None = None
    end_line: int | None = None
    symbol: str | None = None
    anchor: str | None = None
    grep_signature: str | None = None

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
        return data


class EvidenceStore:
    def __init__(self, repo_root: Path | str = "."):
        self.repo_root = Path(repo_root).resolve()
        self.evidence_items: list[CodeEvidence] = []
        self.tool_executions: list[dict[str, Any]] = []

    def add_evidence(
        self,
        path: str,
        snippet: str,
        start_line: int | None = None,
        end_line: int | None = None,
        symbol: str | None = None,
        anchor: str | None = None,
        grep_signature: str | None = None,
        verify_against_disk: bool = False
    ) -> CodeEvidence:
        """Add and validate code evidence triad."""
        clean_snippet, _ = redact_text(snippet.strip())
        if not clean_snippet:
            raise ValueError("Snippet cannot be empty")

        if start_line is not None:
            if start_line < 1:
                raise ValueError(f"start_line must be >= 1 (got {start_line})")
            if end_line is not None and end_line < start_line:
                raise ValueError(f"end_line ({end_line}) cannot be less than start_line ({start_line})")

        if verify_against_disk:
            target_path = self.repo_root / path
            if target_path.is_file():
                file_text = target_path.read_text(encoding="utf-8", errors="replace")
                lines = file_text.splitlines()
                if start_line is not None and end_line is not None:
                    if end_line > len(lines):
                        raise ValueError(f"end_line ({end_line}) exceeds file length ({len(lines)}) in {path}")

        item = CodeEvidence(
            path=path,
            snippet=clean_snippet,
            start_line=start_line,
            end_line=end_line,
            symbol=symbol,
            anchor=anchor,
            grep_signature=grep_signature
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
        redacted_out, _ = redact_text(stdout)
        redacted_err, _ = redact_text(stderr)
        record = {
            "tool_name": tool_name,
            "command": command,
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
