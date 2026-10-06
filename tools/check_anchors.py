"""Report Markdown links whose #fragment matches no heading slug (github-slugger rules).

Usage: python3 tools/check_anchors.py openspec/changes/<change>
"""
import re
import sys
from pathlib import Path

LINK = re.compile(r"\[([^\[\]]*)\]\(([^)\s]*)#([^)\s]+)\)")


def slug(text: str) -> str:
    text = re.sub(r"`([^`]*)`", r"\1", text).strip().lower()
    text = re.sub(r"[^\w\- ]", "", text)
    return text.replace(" ", "-")


def anchors(path: Path) -> set[str]:
    seen: dict[str, int] = {}
    out = set()
    for line in path.read_text().splitlines():
        m = re.match(r"#{1,6}\s+(.*)", line)
        if m:
            s = slug(m.group(1))
            n = seen.get(s, 0)
            seen[s] = n + 1
            out.add(s if n == 0 else f"{s}-{n}")
    return out


def main(change_dir: str) -> int:
    root = Path(change_dir)
    bad = ok = 0
    for md in sorted(root.rglob("*.md")):
        for i, line in enumerate(md.read_text().splitlines(), 1):
            for label, target, frag in LINK.findall(line):
                dest = (md.parent / target).resolve() if target else md
                if dest.exists() and frag in anchors(dest):
                    ok += 1
                else:
                    bad += 1
                    print(f"DANGLING {md.relative_to(root)}:{i} [{label}] -> {target or '(self)'}#{frag}")
    print(f"{ok} resolved, {bad} dangling")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
