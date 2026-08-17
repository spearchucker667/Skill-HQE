#!/usr/bin/env python3
"""Ecosystem manifest and build configuration detector for HQE.

Scans the repository for build manifests, dependency definitions, and CI/CD
configurations across 22+ software ecosystems without silent truncation.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import os
import sys
from pathlib import Path

ECOSYSTEM_PATTERNS: dict[str, list[str]] = {
    "node": [
        "package.json", "package-lock.json", "pnpm-lock.yaml", "pnpm-workspace.yaml",
        "yarn.lock", ".yarnrc", ".yarnrc.yml", "bun.lock", "bun.lockb", "bunfig.toml", ".npmrc"
    ],
    "rust": [
        "Cargo.toml", "Cargo.lock", "rust-toolchain.toml", "rust-toolchain"
    ],
    "python": [
        "pyproject.toml", "setup.py", "setup.cfg", "requirements.txt", "requirements-*.txt",
        "Pipfile", "Pipfile.lock", "poetry.lock", "pdm.lock", "uv.lock", "tox.ini", "flit.ini"
    ],
    "go": [
        "go.mod", "go.sum", "go.work", "go.work.sum", "Gopkg.toml", "Gopkg.lock"
    ],
    "java": [
        "pom.xml", "build.gradle", "settings.gradle", "gradle.properties", "mvnw", "gradlew"
    ],
    "kotlin": [
        "build.gradle.kts", "settings.gradle.kts"
    ],
    "csharp": [
        "*.csproj", "*.fsproj", "*.vbproj", "*.sln", "global.json", "Directory.Build.props",
        "Directory.Build.targets", "nuget.config"
    ],
    "swift": [
        "Package.swift", "Package.resolved", "*.xcodeproj", "*.xcworkspace", "Cartfile", "Podfile", "Podfile.lock"
    ],
    "dart": [
        "pubspec.yaml", "pubspec.lock"
    ],
    "ruby": [
        "Gemfile", "Gemfile.lock", "*.gemspec", ".rubocop.yml"
    ],
    "php": [
        "composer.json", "composer.lock"
    ],
    "c_cpp": [
        "CMakeLists.txt", "meson.build", "Makefile", "configure.ac", "conanfile.txt", "conanfile.py", "vcpkg.json"
    ],
    "docker": [
        "Dockerfile", "Dockerfile.*", "docker-compose.yml", "docker-compose.yaml",
        "compose.yml", "compose.yaml", ".dockerignore"
    ],
    "kubernetes": [
        "Chart.yaml", "values.yaml", "kustomization.yaml", "kustomization.yml"
    ],
    "terraform": [
        "*.tf", "*.tfvars", ".terraform.lock.hcl"
    ],
    "ansible": [
        "playbook.yml", "playbook.yaml", "site.yml", "site.yaml", "ansible.cfg", "hosts"
    ],
    "github_actions": [
        ".github/workflows/*.yml", ".github/workflows/*.yaml", ".github/actions/*"
    ],
    "gitlab_ci": [
        ".gitlab-ci.yml"
    ],
    "circleci": [
        ".circleci/config.yml"
    ],
    "jenkins": [
        "Jenkinsfile", "Jenkinsfile.*"
    ],
    "bazel": [
        "BUILD", "BUILD.bazel", "WORKSPACE", "WORKSPACE.bazel", "MODULE.bazel"
    ],
    "nix": [
        "flake.nix", "flake.lock", "default.nix", "shell.nix"
    ]
}

IGNORED_DIRECTORIES = {
    ".git", "node_modules", "target", "dist", "build", ".venv", "venv",
    "__pycache__", ".pytest_cache", ".idea", ".vscode", "__MACOSX"
}


def detect_manifests(
    root_path: Path,
    max_per_ecosystem: int | None = None,
    max_results: int | None = None
) -> dict:
    """Scan repository for manifest files across ecosystems."""
    root = root_path.resolve()
    if not root.is_dir():
        raise ValueError(f"Target path does not exist or is not a directory: {root}")

    results: dict[str, list[str]] = {}
    total_found = 0
    returned_found = 0
    is_truncated = False

    limit = max_per_ecosystem if max_per_ecosystem is not None else max_results

    # Collect all relative file paths ignoring standard vendor/cache dirs
    all_files: list[str] = []
    for current_root, dirs, files in os.walk(root):
        rel_dir = Path(current_root).relative_to(root)
        rel_dir_str = "" if str(rel_dir) == "." else str(rel_dir).replace("\\", "/") + "/"

        dirs[:] = [d for d in dirs if d not in IGNORED_DIRECTORIES]

        for f in files:
            all_files.append(f"{rel_dir_str}{f}")

    for ecosystem, patterns in ECOSYSTEM_PATTERNS.items():
        matches: list[str] = []
        for file_path in all_files:
            file_name = os.path.basename(file_path)
            for pattern in patterns:
                if "/" in pattern:
                    if fnmatch.fnmatch(file_path, pattern):
                        matches.append(file_path)
                        break
                else:
                    if fnmatch.fnmatch(file_name, pattern):
                        matches.append(file_path)
                        break

        unique_matches = sorted(list(set(matches)))
        count = len(unique_matches)
        if count > 0:
            total_found += count
            if limit is not None and count > limit:
                is_truncated = True
                unique_matches = unique_matches[:limit]
            returned_found += len(unique_matches)
            results[ecosystem] = unique_matches

    return {
        "root": str(root),
        "total_matches": total_found,
        "returned_matches": returned_found,
        "truncated": is_truncated,
        "ecosystems_detected": sorted(list(results.keys())),
        "manifests": results
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Detect manifests and ecosystems in repository.")
    parser.add_argument("path", nargs="?", default=".", help="Repository root path")
    parser.add_argument("--max-per-ecosystem", type=int, default=None, help="Max manifest items returned per ecosystem")
    args = parser.parse_args()

    try:
        data = detect_manifests(Path(args.path), max_per_ecosystem=args.max_per_ecosystem)
        print(json.dumps(data, indent=2))
        return 0
    except Exception as exc:
        print(f"Error detecting manifests: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
