from pathlib import Path
import re
import pytest

ROOT = Path(__file__).resolve().parents[1]
MD_LINK_RE = re.compile(r'\[([^\]]+)\]\((?!https?://|mailto:|#|conversation://)([^)]+)\)')


def test_all_markdown_relative_links_valid():
    broken = []
    for md_file in ROOT.rglob("*.md"):
        rel_str = str(md_file.relative_to(ROOT))
        if any(skip in rel_str for skip in ("HQE_PROTOCOL_SKILL_EMBED_PACKAGE", ".git")):
            continue

        try:
            content = md_file.read_text(encoding="utf-8", errors="replace")
            for match in MD_LINK_RE.finditer(content):
                target_str = match.group(2).split("#")[0].strip()
                if not target_str:
                    continue
                target_path = (md_file.parent / target_str).resolve()
                if not target_path.exists():
                    broken.append(f"{rel_str} -> '{target_str}'")
        except Exception as exc:
            broken.append(f"Error reading {rel_str}: {exc}")

    assert not broken, f"Broken markdown relative links found:\n" + "\n".join(broken)
