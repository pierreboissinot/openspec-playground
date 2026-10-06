# Design

## Context

`bm.py` is a single-file, dependency-free CLI. `main()` splits `argv` by hand into a command and its positional arguments. Bookmarks are a JSON array of `{"url", "title"}` objects in `~/.bm.json`, loaded and saved whole on each run. The project has no tests. For motivation, see proposal.md (Why), and see the specs for the behavior required.

Constraints:
- Existing `~/.bm.json` files must keep working without any migration step.
- The current behavior of `add`, `list` and `rm` for untagged bookmarks must not change. That covers title parsing, output format and the exit status 2 on an unknown command.
- The tool stays stdlib-only.

## Goals / Non-Goals

**Goals:**
- An additive data model, so that old and new files are read and written by both old and new versions of `bm`.
- Small, local changes in `bm.py` that keep its current structure.
- Automated tests for the new behavior and for compatibility with legacy files.

**Non-Goals:**
- Editing or removing tags on existing bookmarks (`bm tag`, `bm untag`).
- Filtering `export` by tag, and importing Netscape HTML.
- Grouping exported bookmarks into folders by tag.
- Recording creation dates, so the export has no `ADD_DATE`.
- Moving to `argparse`, or restructuring into a package.

## Decisions

### D1: Optional `tags` field, no schema version
Each bookmark object may have a `"tags": [<str>, ...]` array. When loading, a missing field means no tags. When saving, the field is written only for bookmarks that have at least one tag, so legacy entries are written back as they were.

Alternatives considered:
- A versioned envelope such as `{"version": 2, "bookmarks": [...]}`. This breaks older `bm` binaries, which expect a top-level array, and it forces a migration.
- Always writing `"tags": []`. This is harmless, but it rewrites every legacy entry on the first save for no benefit.

The current `save()` dumps whole dicts, so an older `bm` that rewrites the file after a new one has added tags keeps those tags.

### D2: Hand-rolled `--tag` extraction instead of argparse
A small helper walks the arguments after the command. It removes each `--tag <value>` pair, collects the values, and returns the remaining positional arguments. `add` and `list` both use it, and `add` builds the title from the remaining words as it does today.

Alternatives considered:
- `argparse` subcommands. These would treat title words that start with `-` as options, replace the `unknown command:` message and exit path with argparse's own, and add a usage format. All of these are visible changes beyond scope.

### D3: Tag normalization rules
Tags are trimmed, lowercased and deduplicated in first-seen order. A tag that is empty, or that contains whitespace or a comma, is rejected with exit status 2, matching the existing usage-error status. Commas are forbidden because the Netscape `TAGS` attribute is comma-separated. Whitespace is forbidden because `list` renders tags as `#tag` tokens separated by spaces. The `list --tag` filter values go through the same normalization, so matching is case-insensitive.

Alternatives considered:
- Case-sensitive tags. These make `Dev` and `dev` silently distinct, which is a common source of confusion in a tool with no tag-editing command.

### D4: AND filtering with stable numbering
`list --tag a --tag b` keeps the bookmarks whose tag set contains every requested tag. Numbering comes from `enumerate` over the full list before filtering, so the numbers shown always match what `rm <n>` expects.

Alternatives considered:
- OR semantics. These are less useful for narrowing a list, and a user can run several `list` commands to cover the OR case.
- Renumbering the filtered results from 1. This would make `rm` delete the wrong bookmark.

### D5: Export rendering
A pure function renders the document from the loaded bookmarks as a single string, and `main()` routes it either to stdout or to the given path, written as UTF-8. URLs, titles and tags are escaped with `html.escape(..., quote=True)`. The bookmarks form one flat `<DL>` list, and tags are emitted as the `TAGS` attribute, which Firefox, Pinboard and similar importers understand. An `OSError` raised while writing the file is caught, reported on stderr and turned into exit status 1.

Alternatives considered:
- One folder (`<H3>`) per tag. A bookmark with several tags would be duplicated across folders, and importers would then create duplicate bookmarks.
- Synthesizing `ADD_DATE` from the export time. This value would be misleading, and importers treat the attribute as optional.

### D6: Stdlib unittest driving `main()`
A new `test_bm.py` imports `bm`, points `bm.STORE` at a temporary file for each test, calls `bm.main([...])`, and captures stdout and stderr with `contextlib.redirect_stdout` and `contextlib.redirect_stderr`. Tests run with `python -m unittest`. Each spec scenario maps to one test.

Alternatives considered:
- pytest. This would add the project's first dependency for little gain at this size.

## Risks / Trade-offs

- [A title word cannot be the literal `--tag`, because it is always taken as the option, per [D2](#d2-hand-rolled---tag-extraction-instead-of-argparse)] → Accept this. It is unlikely in practice, and `--` escaping can be added later if needed.
- [Some importers ignore the `TAGS` attribute, per [D5](#d5-export-rendering)] → Accept this. The links and titles still import, and the attribute is harmless where it is not supported.
- [A hand-edited file may contain tags that are not normalized, which `bm add` never produces under [D3](#d3-tag-normalization-rules)] → Normalize stored tags when comparing them for `list --tag`, so that filtering stays case-insensitive.
- [Tests mutate the `bm.STORE` module global, per [D6](#d6-stdlib-unittest-driving-main)] → Save and restore it in `setUp`/`tearDown` so the real `~/.bm.json` is never touched.

## Migration Plan

No migration is needed, per [D1](#d1-optional-tags-field-no-schema-version). Rolling back to the previous `bm.py` is safe: it reads files that contain `tags`, ignores the field, and keeps it when it rewrites the file.
