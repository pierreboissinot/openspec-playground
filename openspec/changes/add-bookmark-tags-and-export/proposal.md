# Proposal

## Why

`bm` stores a flat list of bookmarks with no way to group them, and there is no way to move them into a browser or another bookmark manager. Tags give users lightweight grouping. Netscape bookmarks HTML export lets them import their bookmarks into Firefox, Chrome, Safari, Pinboard and similar tools. Users already have `~/.bm.json` files, so the new features must not require a migration.

## What Changes

- `bm add <url> [title...]` accepts one or more `--tag <name>` options. The tags are stored on the bookmark.
- `bm list` shows each bookmark's tags. `bm list --tag <name>` (repeatable) shows only the bookmarks that carry every given tag. Each bookmark keeps its position number from the full list, so `bm rm <n>` still targets the right bookmark after filtering.
- New `bm export [path]` command writes every bookmark as a Netscape bookmarks HTML document, including tags. With no path it writes to stdout.
- Existing `~/.bm.json` files that have no tags stay valid and readable. They are not migrated or rewritten until the user changes them.
- Untagged bookmarks keep the same `list` output as today. No change is **BREAKING**.

Assumptions made without asking the user (see design.md for rationale):
- Tags are case-insensitive and stored in lowercase. Whitespace around a tag is trimmed, and a tag cannot be empty or contain whitespace or commas.
- Filtering by several tags uses AND (every tag must match).
- Bookmarks have no creation date, so the export omits `ADD_DATE`.
- Editing or removing tags on an existing bookmark, and filtering the export by tag, are out of scope.

## Capabilities

### New Capabilities
- `bookmark-tags`: attaching tags to bookmarks, showing them, filtering the list by tag, and reading bookmark files written before tags existed.
- `bookmark-export`: exporting bookmarks to the Netscape bookmarks HTML interchange format.

### Modified Capabilities

None. No specs exist yet under `openspec/specs/`.

## Impact

- `bm.py`: argument handling for `add` and `list`, the bookmark record shape (optional `tags` field), and a new `export` command.
- `README.md`: usage for `--tag` and `export`.
- New stdlib `unittest` test module. The project has no tests and no dependencies today, and none are added.
- Data file `~/.bm.json`: gains an optional per-bookmark `tags` array. The change is additive, and older versions of `bm` ignore the field.
