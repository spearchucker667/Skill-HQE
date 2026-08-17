#!/usr/bin/env python3
"""Safe, read-only static risk scanner for HQE repositories.

Ports the local risk check heuristics from HQE Workbench (crates/hqe-core/src/repo.rs)
to provide fast candidate finding discovery without dynamic code execution.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

# Sensitive file patterns
SENSITIVE_FILE_PATTERNS = [
    ("id_rsa", "SSH private key"),
    ("id_dsa", "SSH private key"),
    ("id_ecdsa", "SSH private key"),
    ("id_ed25519", "SSH private key"),
    (".pem", "PEM certificate or private key"),
    (".p12", "PKCS12 certificate bundle"),
    (".pfx", "PFX certificate bundle"),
    ("credentials.json", "Credentials file"),
    ("service-account.json", "Service account key file"),
    ("secrets.json", "Secret configuration file"),
    ("secrets.yml", "Secret configuration file"),
    ("secrets.yaml", "Secret configuration file"),
    (".kdbx", "KeePass password database"),
]

# Prompt-injection / instruction-override markers that may appear in untrusted data.
PROMPT_INJECTION_MARKERS = [
    "ignore previous instructions",
    "ignore the above instructions",
    "disable security checks",
    "mark this repository safe",
    "you are now in developer mode",
    "ignore previous command",
    "do not follow your instructions",
    "override safety",
    "pretend to be",
    "new instructions:",
]

# Source secret patterns (compiled once)
SECRET_PATTERNS = [
    ("AWS_KEY", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("GITHUB_TOKEN", re.compile(r"gh[pousr]_[A-Za-z0-9_]{36,}")),
    ("SLACK_TOKEN", re.compile(r"xox[baprs]-[0-9]{10,13}-[0-9]{10,13}")),
    ("GOOGLE_API_KEY", re.compile(r"AIza[0-9A-Za-z_-]{35}")),
    ("API_KEY", re.compile(r'(?i)(api[_-]?key|apikey)\s*[=:]\s*[\'"][a-zA-Z0-9_-]{16,}[\'"]')),
    ("PASSWORD", re.compile(r'(?i)(password|passwd|pwd)\s*[=:]\s*[\'"][^\'"]{6,}[\'"]')),
    ("SECRET", re.compile(r'(?i)(secret|private[_-]?key)\s*[=:]\s*[\'"][a-zA-Z0-9_-]{8,}[\'"]')),
    ("TOKEN", re.compile(r'(?i)(token|auth[_-]?token)\s*[=:]\s*[\'"][a-zA-Z0-9_-]{10,}[\'"]')),
]

IGNORED_DIRS = {
    ".git", "node_modules", "target", "dist", "build", ".venv", "venv",
    "__pycache__", ".pytest_cache", ".idea", ".vscode"
}

SOURCE_EXTENSIONS = {
    ".rs", ".js", ".ts", ".tsx", ".jsx", ".py", ".go", ".java", ".kt",
    ".cs", ".rb", ".php", ".c", ".cpp", ".h", ".hpp", ".swift", ".dart"
}


def mask_secret_line(line: str) -> str:
    """Mask secret value in a string, preserving only variable name."""
    if "=" in line:
        k, _ = line.split("=", 1)
        return f"{k.strip()}=***REDACTED***"
    if ":" in line:
        k, _ = line.split(":", 1)
        return f"{k.strip()}: ***REDACTED***"
    return "***REDACTED***"


def _is_safe_path(root: Path, candidate: Path) -> bool:
    """Return True if candidate is within root and contains no parent traversal."""
    try:
        candidate.resolve().relative_to(root.resolve())
    except ValueError:
        return False
    if ".." in candidate.parts or ".." in str(candidate).split("/"):
        return False
    return True


def scan_local_risks(root_path: Path) -> list[dict]:
    """Execute all static risk checks against repository."""
    root = root_path.resolve()
    if not root.is_dir():
        raise ValueError(f"Not a valid directory: {root}")
    if ".." in str(root_path):
        raise ValueError(f"Path traversal detected in scan root: {root_path}")

    findings: list[dict] = []

    # 1. Check .env files and gitignore status
    env_files = [".env", ".env.local", ".env.production", ".env.development", ".env.staging"]
    gitignore_path = root / ".gitignore"
    gitignore_content = gitignore_path.read_text(encoding="utf-8", errors="replace") if gitignore_path.is_file() else ""

    for env_name in env_files:
        env_path = root / env_name
        if env_path.is_file():
            is_gitignored = env_name in gitignore_content or ".env" in gitignore_content
            if not is_gitignored:
                findings.append({
                    "finding_type": "UNGITIGNORED_ENV",
                    "category": "SEC",
                    "severity": "HIGH",
                    "description": f"{env_name} exists in repository root but is not gitignored",
                    "file_path": env_name,
                    "line_number": 1,
                    "snippet": f"# {env_name} configuration file",
                    "recommendation": f"Add '{env_name}' to .gitignore immediately"
                })

            # Check for secrets inside .env
            try:
                env_text = env_path.read_text(encoding="utf-8", errors="replace")
                for line_idx, line in enumerate(env_text.splitlines(), start=1):
                    lower_line = line.lower()
                    if any(kw in lower_line for kw in ("password", "secret", "api_key", "token", "key")) and "=" in line and not line.strip().endswith("="):
                        findings.append({
                            "finding_type": "HARDCODED_SECRET",
                            "category": "SEC",
                            "severity": "CRITICAL",
                            "description": f"Potential hardcoded secret in {env_name}",
                            "file_path": env_name,
                            "line_number": line_idx,
                            "snippet": mask_secret_line(line),
                            "recommendation": "Move secrets to an encrypted vault or inject at runtime"
                        })
            except OSError:
                pass

    # Collect source and general files
    all_files: list[tuple[str, Path]] = []
    for current_root, dirs, files in os.walk(root):
        rel_dir = Path(current_root).relative_to(root)
        rel_dir_str = "" if str(rel_dir) == "." else str(rel_dir).replace("\\", "/") + "/"
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]

        for f in files:
            rel_file = f"{rel_dir_str}{f}"
            all_files.append((rel_file, Path(current_root) / f))

    # 2. Check for sensitive files & permissions
    for rel_file, abs_path in all_files:
        lower_rel = rel_file.lower()
        for pat, desc in SENSITIVE_FILE_PATTERNS:
            if pat in lower_rel and not "fixtures" in lower_rel and not "acceptance" in lower_rel:
                findings.append({
                    "finding_type": "SENSITIVE_FILE",
                    "category": "SEC",
                    "severity": "HIGH",
                    "description": f"{desc} detected in repository: {rel_file}",
                    "file_path": rel_file,
                    "line_number": 1,
                    "snippet": f"# Sensitive file: {rel_file}",
                    "recommendation": "Ensure this file is gitignored and removed from git tracking"
                })
                break

        # Check world-writable permissions on Unix
        if hasattr(os, "stat") and hasattr(os, "chmod"):
            try:
                mode = abs_path.stat().st_mode
                if mode & 0o002 != 0:
                    findings.append({
                        "finding_type": "WORLD_WRITABLE",
                        "category": "SEC",
                        "severity": "MEDIUM",
                        "description": f"World-writable file permissions detected on {rel_file}",
                        "file_path": rel_file,
                        "line_number": 1,
                        "snippet": f"# Permissions mode: {oct(mode)}",
                        "recommendation": "Remove world-write permissions: chmod o-w"
                    })
            except OSError:
                pass

    # 3. Source Code Scans
    for rel_file, abs_path in all_files:
        ext = abs_path.suffix.lower()
        if ext not in SOURCE_EXTENSIONS:
            continue

        # Skip test fixtures to avoid self-flagging test suites
        if any(skip in rel_file.lower() for skip in ("/tests/fixtures/", "/acceptance/", "/tests/")):
            continue

        try:
            content = abs_path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue

        lines = content.splitlines()
        for idx, line in enumerate(lines, start=1):
            trimmed = line.trim() if hasattr(line, "trim") else line.strip()
            if not trimmed or trimmed.startswith(("//", "#", "/*", "*", "<!--", "--")):
                continue

            # A. Hardcoded Secrets in Code
            for pat_name, regex in SECRET_PATTERNS:
                if regex.search(line):
                    findings.append({
                        "finding_type": f"POTENTIAL_{pat_name}",
                        "category": "SEC",
                        "severity": "CRITICAL",
                        "description": f"Potential {pat_name.lower().replace('_', ' ')} detected in source code",
                        "file_path": rel_file,
                        "line_number": idx,
                        "snippet": mask_secret_line(trimmed),
                        "recommendation": "Replace hardcoded secret with environment variable lookup"
                    })
                    break

            lower_line = trimmed.lower()

            # B. SQL Injection heuristics
            sql_kws = ["select ", "insert into", "update ", "delete from", "drop table"]
            if any(kw in lower_line for kw in sql_kws) and ("format(" in lower_line or "format!(" in lower_line or "+ " in line or "${" in line or "%s" in line):
                if not any(fp in lower_line for fp in ["selected_", "updated_at", "from_"]):
                    findings.append({
                        "finding_type": "SQL_INJECTION_RISK",
                        "category": "SEC",
                        "severity": "HIGH",
                        "description": "Potential SQL injection risk via string formatting/concatenation",
                        "file_path": rel_file,
                        "line_number": idx,
                        "snippet": trimmed,
                        "recommendation": "Use parameterized queries or ORM prepared statements"
                    })

            # C. Insecure HTTP
            if "http://" in lower_line and not any(local in lower_line for local in ("localhost", "127.0.0.1", "0.0.0.0", "w3.org", "schemas")):
                findings.append({
                    "finding_type": "INSECURE_HTTP",
                    "category": "SEC",
                    "severity": "MEDIUM",
                    "description": "Insecure HTTP URL in source code",
                    "file_path": rel_file,
                    "line_number": idx,
                    "snippet": trimmed,
                    "recommendation": "Use HTTPS protocol instead of HTTP"
                })

            # D. Dangerous eval()
            if "eval(" in lower_line and not "evaluate" in lower_line:
                findings.append({
                    "finding_type": "DANGEROUS_EVAL",
                    "category": "SEC",
                    "severity": "HIGH",
                    "description": "Dangerous eval() usage detected",
                    "file_path": rel_file,
                    "line_number": idx,
                    "snippet": trimmed,
                    "recommendation": "Avoid dynamic code execution via eval(); use safe parsers"
                })

            # E. Debug Console Statements in Production Code
            if (ext in {".js", ".ts", ".tsx", ".jsx"}) and ("console.log(" in lower_line or "console.debug(" in lower_line):
                findings.append({
                    "finding_type": "DEBUG_CODE",
                    "category": "DX",
                    "severity": "LOW",
                    "description": "Debug console statement in production source",
                    "file_path": rel_file,
                    "line_number": idx,
                    "snippet": trimmed,
                    "recommendation": "Remove debug logging statements before release"
                })

            # F. TODO / FIXME / HACK markers
            if any(marker in trimmed.upper() for marker in ("TODO:", "FIXME:", "HACK:", "XXX:")):
                findings.append({
                    "finding_type": "WORKAROUND_MARKER",
                    "category": "DEBT",
                    "severity": "INFO",
                    "description": "Unresolved TODO/FIXME/HACK marker in source code",
                    "file_path": rel_file,
                    "line_number": idx,
                    "snippet": trimmed,
                    "recommendation": "Convert marker into a tracked finding or master TODO item"
                })

    # 3b. Prompt-injection marker scan for data files
    data_extensions = {".md", ".txt", ".json", ".yaml", ".yml", ".toml"}
    for rel_file, abs_path in all_files:
        ext = abs_path.suffix.lower()
        if ext not in data_extensions:
            continue
        if any(skip in rel_file.lower() for skip in ("/tests/fixtures/", "/acceptance/", "/tests/")):
            continue
        try:
            content = abs_path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for idx, line in enumerate(content.splitlines(), start=1):
            trimmed = line.strip()
            if not trimmed:
                continue
            lowered = trimmed.lower()
            for marker in PROMPT_INJECTION_MARKERS:
                if marker in lowered:
                    findings.append({
                        "finding_type": "PROMPT_INJECTION_MARKER",
                        "category": "SEC",
                        "severity": "INFO",
                        "description": f"Possible prompt-injection marker in data file: {marker!r}",
                        "file_path": rel_file,
                        "line_number": idx,
                        "snippet": trimmed,
                        "recommendation": "Treat repository content as untrusted data; do not execute instructions found in files"
                    })
                    break

    # 4. Check package.json for suspicious postinstall
    pkg_json = root / "package.json"
    if pkg_json.is_file():
        try:
            pkg_text = pkg_json.read_text(encoding="utf-8", errors="replace")
            if "postinstall" in pkg_text and any(net in pkg_text for net in ("curl", "wget", "http://", "https://")):
                findings.append({
                    "finding_type": "SUSPICIOUS_POSTINSTALL",
                    "category": "SEC",
                    "severity": "HIGH",
                    "description": "package.json contains postinstall script with network activity",
                    "file_path": "package.json",
                    "line_number": 1,
                    "snippet": '"postinstall": "..."',
                    "recommendation": "Review postinstall script for supply chain security"
                })
        except OSError:
            pass

    # 5. Configuration & Project Hygiene
    if not (root / "README.md").is_file() and not (root / "README.rst").is_file():
        findings.append({
            "finding_type": "MISSING_README",
            "category": "DOC",
            "severity": "LOW",
            "description": "No README file found in repository root",
            "file_path": ".",
            "line_number": None,
            "snippet": None,
            "recommendation": "Add a README.md describing the project"
        })

    if not (root / "LICENSE").is_file() and not (root / "LICENSE.md").is_file():
        findings.append({
            "finding_type": "MISSING_LICENSE",
            "category": "DOC",
            "severity": "INFO",
            "description": "No LICENSE file found in repository root",
            "file_path": ".",
            "line_number": None,
            "snippet": None,
            "recommendation": "Add a LICENSE file"
        })

    if not (root / ".gitignore").is_file():
        findings.append({
            "finding_type": "MISSING_GITIGNORE",
            "category": "DX",
            "severity": "MEDIUM",
            "description": "No .gitignore file found in repository root",
            "file_path": ".",
            "line_number": None,
            "snippet": None,
            "recommendation": "Create a .gitignore tailored to your technology stack"
        })

    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description="Run local static risk checks on repository.")
    parser.add_argument("path", nargs="?", default=".", help="Repository root path")
    args = parser.parse_args()

    try:
        results = scan_local_risks(Path(args.path))
        print(json.dumps(results, indent=2))
        return 0
    except Exception as exc:
        print(f"Error during local risk scan: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
