"""Run manifest generation engine conforming to schemas/run-manifest.schema.json."""

from __future__ import annotations

import datetime
import json
import subprocess
from pathlib import Path
from typing import Any

import yaml

from .finding_registry import FindingRegistry
from .evidence_store import EvidenceStore
from .health_scoring import HealthScore, compute_health_score, score_to_band


_PROTOCOL_YAML = Path(__file__).resolve().parents[1] / "protocol" / "hqe-engineer.yaml"


def _derive_protocol_version() -> str:
    """Read the canonical protocol version from the HQE protocol YAML."""
    try:
        data = yaml.safe_load(_PROTOCOL_YAML.read_text(encoding="utf-8"))
        version = data.get("protocol_version") or data.get("schema_version")
        if version:
            return str(version)
    except Exception:
        pass
    return "5.0.0"


def _derive_protocol_name() -> str:
    """Read the canonical protocol name from the HQE protocol YAML."""
    try:
        data = yaml.safe_load(_PROTOCOL_YAML.read_text(encoding="utf-8"))
        name = (
            data.get("meta", {}).get("name")
            or data.get("name")
            or "HQE Engineer Protocol"
        )
        if name:
            return str(name)
    except Exception:
        pass
    return "HQE Engineer Protocol"


class RunManifestGenerator:
    def __init__(
        self,
        repo_path: Path | str = ".",
        mode: str = "audit",
        run_id: str | None = None
    ):
        self.repo_path = Path(repo_path).resolve()
        self.mode = mode
        self.run_id = run_id or f"hqe-run-{datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%d-%H%M%S')}"
        self.start_time = datetime.datetime.now(datetime.timezone.utc).isoformat()
        self.end_time: str | None = None

    def _get_git_commit(self) -> str:
        try:
            res = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=5
            )
            if res.returncode == 0:
                return res.stdout.strip()
        except Exception:
            pass
        return "unknown"

    def build_manifest(
        self,
        registry: FindingRegistry,
        evidence_store: EvidenceStore | None = None,
        total_files: int = 0,
        health_score: int | HealthScore | None = None,
        health_reasons: list[str] | None = None,
        subsystems_coverage: list[dict[str, Any]] | None = None,
        unreviewed_surfaces: list[str] | None = None
    ) -> dict[str, Any]:
        """Assemble full run manifest dict.

        Coverage defaults are truthful: a subsystem is not claimed as fully
        reviewed unless explicitly provided.  When no health score is supplied,
        a coverage-aware score is computed from the registry and the (truthful)
        coverage defaults.
        """
        self.end_time = datetime.datetime.now(datetime.timezone.utc).isoformat()
        sev_counts = registry.count_by_severity()

        if subsystems_coverage is None:
            subsystems_coverage = [
                {
                    "subsystem": "root",
                    "files": total_files,
                    "reviewed": False,
                    "depth": "unknown",
                    "findings_count": len(registry.findings)
                }
            ]

        unreviewed_surfaces = unreviewed_surfaces or [
            "Coverage not established; surfaces may be unreviewed"
        ]

        # Resolve health score.
        if health_score is None:
            coverage_known = all(s.get("reviewed") for s in subsystems_coverage)
            health_score = compute_health_score(
                registry.findings.values(),
                coverage_known=coverage_known,
                coverage_depth=subsystems_coverage[0].get("depth", "unknown"),
                unreviewed_surfaces=unreviewed_surfaces,
            )
        elif isinstance(health_score, int):
            health_score = HealthScore(
                score=health_score,
                omitted=False,
                reasons=health_reasons or ["Evaluated against HQE v5 rubric"],
            )

        # Build command representations.
        tool_records = evidence_store.tool_executions if evidence_store else []
        command_strings = [t["command"] for t in tool_records]
        command_records = [
            {
                "tool": t["tool_name"],
                "command": t["command"],
                "exit_code": t["exit_code"],
                "result": "success" if t["exit_code"] == 0 else "failure",
            }
            for t in tool_records
        ]

        manifest: dict[str, Any] = {
            "run_id": self.run_id,
            "timestamp": self.start_time,
            "timestamps": {
                "start": self.start_time,
                "end": self.end_time
            },
            "repository_path": str(self.repo_path),
            "repository_details": {
                "commit": self._get_git_commit(),
                "path": str(self.repo_path)
            },
            "protocol_details": {
                "name": _derive_protocol_name(),
                "version": _derive_protocol_version()
            },
            "environment": {
                "python_version": f"{subprocess.sys.version_info.major}.{subprocess.sys.version_info.minor}.{subprocess.sys.version_info.micro}",
                "platform": subprocess.sys.platform
            },
            "commands": command_strings,
            "command_records": command_records,
            "limits": {
                "max_files": 1000
            },
            "mode": self.mode,
            "coverage": subsystems_coverage,
            "unreviewed_surfaces": unreviewed_surfaces,
            "summary": {
                "total_files_scanned": total_files,
                "total_findings": len(registry.findings),
                "critical_findings": sev_counts.get("CRITICAL", 0),
                "high_findings": sev_counts.get("HIGH", 0),
                "medium_findings": sev_counts.get("MEDIUM", 0),
                "low_findings": sev_counts.get("LOW", 0),
                "info_findings": sev_counts.get("INFO", 0)
            }
        }

        hs = health_score
        health_entry: dict[str, Any] = {
            "band": score_to_band(hs.score) if hs.score is not None else "Unknown",
            "omitted": hs.omitted,
            "reasons": health_reasons or hs.reasons,
        }
        if hs.score is not None:
            health_entry["score"] = hs.score
        manifest["health_score"] = health_entry

        return manifest

    def save_to_file(self, manifest_data: dict[str, Any], target_path: Path | str = "HQE_RUN_MANIFEST.json") -> Path:
        out_path = Path(target_path).resolve()
        with out_path.open("w", encoding="utf-8") as fh:
            json.dump(manifest_data, fh, indent=2)
        return out_path
