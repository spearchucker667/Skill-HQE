"""Run manifest generation engine conforming to schemas/run-manifest.schema.json."""

from __future__ import annotations

import datetime
import json
import subprocess
from pathlib import Path
from typing import Any

from .finding_registry import FindingRegistry
from .evidence_store import EvidenceStore


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
        health_score: int | None = None,
        health_reasons: list[str] | None = None,
        subsystems_coverage: list[dict[str, Any]] | None = None
    ) -> dict[str, Any]:
        """Assemble full run manifest dict."""
        self.end_time = datetime.datetime.now(datetime.timezone.utc).isoformat()
        sev_counts = registry.count_by_severity()

        score_band = None
        if health_score is not None:
            if health_score >= 9:
                score_band = "Exceptional"
            elif health_score >= 7:
                score_band = "Solid"
            elif health_score >= 5:
                score_band = "Adequate"
            elif health_score >= 3:
                score_band = "Concerning"
            else:
                score_band = "Critical Risk"

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
                "name": "HQE Engineer Protocol",
                "version": "5.0.0"
            },
            "environment": {
                "python_version": f"{subprocess.sys.version_info.major}.{subprocess.sys.version_info.minor}.{subprocess.sys.version_info.micro}",
                "platform": subprocess.sys.platform
            },
            "commands": [t["command"] for t in (evidence_store.tool_executions if evidence_store else [])],
            "limits": {
                "max_files": 1000
            },
            "mode": self.mode,
            "coverage": subsystems_coverage or [
                {
                    "subsystem": "root",
                    "files": total_files,
                    "reviewed": True,
                    "depth": "full",
                    "findings_count": len(registry.findings)
                }
            ],
            "unreviewed_surfaces": [],
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

        if health_score is not None:
            manifest["health_score"] = {
                "score": health_score,
                "band": score_band or "Solid",
                "omitted": False,
                "reasons": health_reasons or ["Evaluated against HQE v5 rubric"]
            }

        return manifest

    def save_to_file(self, manifest_data: dict[str, Any], target_path: Path | str = "HQE_RUN_MANIFEST.json") -> Path:
        out_path = Path(target_path).resolve()
        with out_path.open("w", encoding="utf-8") as fh:
            json.dump(manifest_data, fh, indent=2)
        return out_path
