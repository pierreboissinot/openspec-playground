#!/usr/bin/env python3
import json
import sys
from pathlib import Path

STORE = Path.home() / ".bm.json"


def load() -> list[dict]:
    return json.loads(STORE.read_text()) if STORE.exists() else []


def save(items: list[dict]) -> None:
    STORE.write_text(json.dumps(items, indent=2))


def main(argv: list[str]) -> int:
    cmd, *args = argv or ["list"]
    items = load()
    if cmd == "add":
        items.append({"url": args[0], "title": " ".join(args[1:]) or args[0]})
        save(items)
    elif cmd == "list":
        for i, it in enumerate(items, 1):
            print(f"{i}. {it['title']} <{it['url']}>")
    elif cmd == "rm":
        items.pop(int(args[0]) - 1)
        save(items)
    else:
        print(f"unknown command: {cmd}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
