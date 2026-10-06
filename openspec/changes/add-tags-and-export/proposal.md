# Proposal

## Why

`bm` stores a flat list of bookmarks with no way to group them, and the only way to get them out is reading `~/.bm.json` by hand. Tags make a growing list navigable, and a Netscape bookmarks HTML export lets users import their bookmarks into any browser or bookmark manager.

## What Changes

- `bm add <url> [title...] --tag <name>` attaches one or more tags to a new bookmark (`--tag` is repeatable; `--tag=<name>` also accepted).
- `bm list --tag <name>` shows only bookmarks carrying that tag; repeating `--tag` narrows the result (all given tags must match).
- `bm list` displays a bookmark's tags after its URL when it has any; untagged bookmarks print exactly as today.
- Filtered `list` keeps each bookmark's original position number, so the number shown remains valid for `bm rm`.
- New `bm export [PATH]` command writes a Netscape bookmarks HTML file (the `NETSCAPE-Bookmark-file-1` format browsers import), including tags in the `TAGS` attribute. Without `PATH` it writes to stdout.
- Existing `~/.bm.json` files (entries with only `url` and `title`) load and work unchanged; a missing `tags` field means "no tags". No migration step, no rewrite of the file on read.
- Invalid tag usage (missing value, empty tag, tag containing a comma) is rejected with an error on stderr and exit code 2, without modifying the store.

Out of scope: editing tags on existing bookmarks, filtering `export` by tag, importing HTML, storing or exporting creation dates, folder hierarchies in the export.

## Capabilities

### New Capabilities
- `bookmark-tags`: attaching tags to bookmarks, filtering the listing by tag, and backward-compatible handling of stored bookmarks that predate tags.
- `bookmark-export`: exporting the bookmark collection to a Netscape bookmarks HTML document.

### Modified Capabilities
<!-- None: no specs exist yet under openspec/specs/. -->

## Impact

- `bm.py`: argument handling for `add` and `list`, new `export` command, HTML rendering. Standard library only (`html` module for escaping); no new dependencies.
- `~/.bm.json` format: additive optional `tags` array per entry. Files written by the new version remain readable by the old version (it ignores unknown keys).
- `README.md`: document `--tag` and `export`.
- New `test_bm.py` (stdlib `unittest`) — the project currently has no tests.
