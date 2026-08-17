#!/usr/bin/env python3
"""Detect test, lint, typecheck, build, and security verification commands from manifests."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path


def detect_commands(root_path: Path) -> list[dict]:
    """Detect available verification and test commands across manifest files."""
    root = root_path.resolve()
    commands: list[dict] = []

    # 1. Node.js (package.json)
    pkg_path = root / "package.json"
    if pkg_path.is_file():
        try:
            with pkg_path.open("r", encoding="utf-8") as fh:
                pkg_data = json.load(fh)
            scripts = pkg_data.get("scripts", {})
            for script_name, script_cmd in scripts.items():
                lower_name = script_name.lower()
                kind = None
                if "test" in lower_name or "spec" in lower_name or "jest" in lower_name or "vitest" in lower_name:
                    kind = "test"
                elif "lint" in lower_name or "eslint" in lower_name:
                    kind = "lint"
                elif "typecheck" in lower_name or "tsc" in lower_name or "types" in lower_name:
                    kind = "typecheck"
                elif "format" in lower_name or "prettier" in lower_name:
                    kind = "format-check"
                elif "build" in lower_name or "compile" in lower_name:
                    kind = "build"
                elif "audit" in lower_name or "security" in lower_name:
                    kind = "security"

                if kind:
                    commands.append({
                        "command": f"npm run {script_name}",
                        "kind": kind,
                        "source": f"package.json#scripts.{script_name}",
                        "raw_script": script_cmd,
                        "executed": False
                    })
        except Exception:
            pass

    # 2. Rust (Cargo.toml)
    cargo_path = root / "Cargo.toml"
    if cargo_path.is_file():
        commands.append({
            "command": "cargo test --all-targets",
            "kind": "test",
            "source": "Cargo.toml",
            "executed": False
        })
        commands.append({
            "command": "cargo clippy --all-targets -- -D warnings",
            "kind": "lint",
            "source": "Cargo.toml",
            "executed": False
        })
        commands.append({
            "command": "cargo check --all-targets",
            "kind": "typecheck",
            "source": "Cargo.toml",
            "executed": False
        })
        commands.append({
            "command": "cargo fmt --check",
            "kind": "format-check",
            "source": "Cargo.toml",
            "executed": False
        })
        commands.append({
            "command": "cargo build --all-targets",
            "kind": "build",
            "source": "Cargo.toml",
            "executed": False
        })

    # 3. Python (pyproject.toml, pytest.ini, tox.ini, setup.py, requirements)
    pyproject_path = root / "pyproject.toml"
    has_pytest = (root / "pytest.ini").is_file() or (root / "conftest.py").is_file() or (root / "tests").is_dir()

    if pyproject_path.is_file():
        try:
            content = pyproject_path.read_text(encoding="utf-8", errors="replace")
            if "pytest" in content or has_pytest:
                commands.append({
                    "command": "pytest",
                    "kind": "test",
                    "source": "pyproject.toml",
                    "executed": False
                })
            if "ruff" in content:
                commands.append({
                    "command": "ruff check .",
                    "kind": "lint",
                    "source": "pyproject.toml#tool.ruff",
                    "executed": False
                })
            if "mypy" in content:
                commands.append({
                    "command": "mypy .",
                    "kind": "typecheck",
                    "source": "pyproject.toml#tool.mypy",
                    "executed": False
                })
            if "black" in content:
                commands.append({
                    "command": "black --check .",
                    "kind": "format-check",
                    "source": "pyproject.toml#tool.black",
                    "executed": False
                })
        except Exception:
            pass
    elif has_pytest:
        commands.append({
            "command": "pytest",
            "kind": "test",
            "source": "tests/",
            "executed": False
        })

    # 4. Go (go.mod)
    if (root / "go.mod").is_file():
        commands.append({
            "command": "go test ./...",
            "kind": "test",
            "source": "go.mod",
            "executed": False
        })
        commands.append({
            "command": "golangci-lint run",
            "kind": "lint",
            "source": "go.mod",
            "executed": False
        })
        commands.append({
            "command": "go build ./...",
            "kind": "build",
            "source": "go.mod",
            "executed": False
        })

    # 5. Makefile
    makefile = root / "Makefile"
    if makefile.is_file():
        try:
            with makefile.open("r", encoding="utf-8", errors="replace") as fh:
                for line in fh:
                    line = line.strip()
                    if line.endswith(":") and not line.startswith((".", "#", "\t", " ")):
                        target = line[:-1].strip()
                        if target in ("test", "check", "unit-test", "integration-test"):
                            commands.append({
                                "command": f"make {target}",
                                "kind": "test",
                                "source": f"Makefile#{target}",
                                "executed": False
                            })
                        elif target in ("lint", "clippy", "flake8", "eslint"):
                            commands.append({
                                "command": f"make {target}",
                                "kind": "lint",
                                "source": f"Makefile#{target}",
                                "executed": False
                            })
                        elif target in ("build", "compile", "all"):
                            commands.append({
                                "command": f"make {target}",
                                "kind": "build",
                                "source": f"Makefile#{target}",
                                "executed": False
                            })
        except Exception:
            pass

    return commands


def main() -> int:
    parser = argparse.ArgumentParser(description="Detect test, lint, and verification commands.")
    parser.add_argument("path", nargs="?", default=".", help="Repository root path")
    args = parser.parse_args()

    try:
        cmds = detect_commands(Path(args.path))
        print(json.dumps(cmds, indent=2))
        return 0
    except Exception as exc:
        print(f"Error detecting commands: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
