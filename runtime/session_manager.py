"""Session state machine and persistence manager for HQE."""

from __future__ import annotations

import datetime
import json
from enum import Enum
from pathlib import Path
from typing import Any


class SessionState(str, Enum):
    INIT = "INIT"
    ORIENTED = "ORIENTED"
    TRIAGED = "TRIAGED"
    SCANNING = "SCANNING"
    REMEDIATING = "REMEDIATING"
    VERIFYING = "VERIFYING"
    COMPLETED = "COMPLETED"
    ABORTED_INCIDENT = "ABORTED_INCIDENT"


class SessionManager:
    def __init__(self, session_id: str | None = None, repo_path: str = "."):
        now_str = datetime.datetime.now(datetime.timezone.utc).isoformat()
        self.session_id = session_id or f"hqe-session-{datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%d-%H%M%S')}"
        self.started_at = now_str
        self.ended_at: str | None = None
        self.repository_path = str(Path(repo_path).resolve())
        self.state = SessionState.INIT

        self.completed: list[str] = []
        self.in_progress: list[str] = []
        self.discovered: list[str] = []
        # session-log.schema.json requires an array of strings.
        self.reprioritized: list[str] = []
        self.next_session: list[str] = []
        self.events: list[dict[str, Any]] = []

    def log_event(self, level: str, message: str) -> None:
        """Record timestamped lifecycle event matching session-log schema."""
        valid_level = level if level in ("DEBUG", "INFO", "WARN", "ERROR") else "INFO"
        self.events.append({
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "level": valid_level,
            "message": message
        })

    def transition_to(self, new_state: SessionState | str, reason: str = "") -> None:
        """Transition state machine."""
        if isinstance(new_state, str):
            new_state = SessionState(new_state)
        old_state = self.state
        self.state = new_state
        self.log_event("INFO", f"Transitioned from {old_state.value} to {new_state.value}: {reason}")

    def mark_completed(self, item: str) -> None:
        if item in self.in_progress:
            self.in_progress.remove(item)
        if item not in self.completed:
            self.completed.append(item)
        self.log_event("INFO", f"Completed goal: {item}")

    def mark_in_progress(self, item: str) -> None:
        if item not in self.in_progress:
            self.in_progress.append(item)
        self.log_event("INFO", f"Started goal: {item}")

    def add_discovered(self, finding_id: str) -> None:
        if finding_id not in self.discovered:
            self.discovered.append(finding_id)
        self.log_event("INFO", f"Discovered finding: {finding_id}")

    def add_next_session(self, task: str) -> None:
        if task not in self.next_session:
            self.next_session.append(task)

    def finish(self) -> None:
        self.ended_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
        if self.state != SessionState.ABORTED_INCIDENT:
            self.state = SessionState.COMPLETED
        self.log_event("INFO", f"Session finished with state: {self.state.value}")

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "session_id": self.session_id,
            "started_at": self.started_at,
            "repository_path": self.repository_path,
            "state": self.state.value,
            "completed": list(self.completed),
            "in_progress": list(self.in_progress),
            "discovered": list(self.discovered),
            "reprioritized": list(self.reprioritized),
            "next_session": list(self.next_session),
            "events": list(self.events)
        }
        if self.ended_at:
            data["ended_at"] = self.ended_at
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SessionManager":
        """Rebuild a SessionManager from a serialized session log dict.

        Restores run/session identity, timestamps, repository path, lifecycle
        state, and progress lists so saved sessions remain continuous.
        """
        session = cls(
            session_id=data.get("session_id"),
            repo_path=data.get("repository_path", "."),
        )
        if data.get("started_at"):
            session.started_at = data["started_at"]
        session.ended_at = data.get("ended_at")
        state = data.get("state")
        if state:
            try:
                session.state = SessionState(state)
            except ValueError:
                session.log_event("WARN", f"Unknown serialized state {state!r}; kept {session.state.value}")
        session.completed = list(data.get("completed", []))
        session.in_progress = list(data.get("in_progress", []))
        session.discovered = list(data.get("discovered", []))
        reprioritized = data.get("reprioritized", [])
        session.reprioritized = [str(item) for item in reprioritized]
        session.next_session = list(data.get("next_session", []))
        session.events = list(data.get("events", []))
        return session

    @classmethod
    def load_from_file(cls, path: Path | str) -> "SessionManager":
        """Load a serialized session log from disk."""
        with Path(path).open("r", encoding="utf-8") as fh:
            data = json.load(fh)
        if not isinstance(data, dict):
            raise ValueError("Session log must be a JSON object")
        return cls.from_dict(data)

    def save_to_file(self, target_path: Path | str = "HQE_SESSION_LOG.json") -> Path:
        out_path = Path(target_path).resolve()
        with out_path.open("w", encoding="utf-8") as fh:
            json.dump(self.to_dict(), fh, indent=2)
        return out_path
