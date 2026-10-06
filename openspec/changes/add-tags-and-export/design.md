# Design

## Context

`bm.py` is a single ~40-line script: `main()` dispatches on the first argument, positional arguments are read straight from `args`, and the store is a JSON array of `{"url", "title"}` objects at `STORE = Path.home() / ".bm.json"`, read by `load()` and written whole by `save()`. There is no argument parser, no test suite, and no dependency beyond the standard library. Users already have stores in the old shape (see proposal.md — Why; requirements in `specs/bookmark-tags` and `specs/bookmark-export`).

## Goals / Non-Goals

**Goals:**
- Keep the script single-file and stdlib-only.
- Leave every existing invocation (`add`, `list`, `rm`, no-argument `list`, unknown-command error) byte-for-byte identical when `--tag` is not used.
- Keep the store readable by the previous version of `bm`.

**Non-Goals:**
- Introducing a store schema version or migration machinery.
- Restructuring `main()` into a command framework.

## Decisions

### Extract `--tag` options with a small helper instead of switching to `argparse`
A helper takes the argument list and returns the collected tags plus the remaining positional arguments, accepting `--tag NAME` and `--tag=NAME` anywhere. It normalizes each value (strip, lowercase, de-duplicate in first-seen order) and raises a usage error for a missing value, an empty tag, or a comma. `main()` catches that error, prints it to stderr and returns 2 — the exit code already used for unknown commands. Both `add` and `list` use the helper.

*Alternative — `argparse` subparsers:* cleaner for a larger CLI, but it would change usage/error output and exit behaviour for existing commands, and would interpret title words starting with `-` as options (`bm add URL -- my title`). The helper keeps the current loose positional handling intact.

### Store tags as an optional `tags` array, omitted when empty
Entries gain a `tags` list only when the bookmark has tags. All reads go through `entry.get("tags", [])`. Untagged bookmarks added by the new version are therefore identical to those written by the old version, and the old version — which only reads `url` and `title` — keeps working on files written by the new one. Read-only commands (`list`, `export`) never call `save()`, so an old file is not rewritten just by being read.

*Alternative — always write `"tags": []` or normalize the whole file on load:* uniform shape, but it rewrites users' files and adds a migration concern for no behavioural gain.

### Filter by original position
`list` enumerates the full collection first and filters afterwards, so the printed number is the index `rm` expects. Matching is "all requested tags are a subset of the bookmark's tags".

### Render the Netscape document by string building with `html.escape`
The format is a fixed, flat template (DOCTYPE, META, TITLE, H1, one `<DL><p>` with one `<DT><A ...>` line per bookmark, indented four spaces). A pure function turns the bookmark list into the document string; `html.escape(..., quote=True)` is applied to the URL, title and joined tags. No `ADD_DATE` attribute is emitted because the store holds no timestamps; importers treat it as optional.

*Alternative — an HTML/XML library:* the Netscape format is not valid XML/HTML5 (unclosed `<DT>`, `<p>`), so a generic serializer would fight the format rather than help.

### Emit UTF-8 regardless of locale
The file path is written with `write_text(..., encoding="utf-8")`. Stdout output is written as UTF-8 bytes to `sys.stdout.buffer`, so the bytes always match the declared `charset=UTF-8` even under a non-UTF-8 locale. An `OSError` while writing the file is reported as `bm: cannot write <path>: <reason>` on stderr with exit code 1.

### Tests with stdlib `unittest`
A new `test_bm.py` exercises `main()` in-process with `bm.STORE` pointed at a temporary file and stdout/stderr captured, plus the rendering function directly. The stdout export path, which writes to `sys.stdout.buffer`, is covered by running `bm.py` as a subprocess with `HOME` set to a temporary directory. Run with `python -m unittest`.

## Risks / Trade-offs

- [Tags are lowercased, so a user's chosen casing is lost] → Accepted for predictable filtering; documented in the README.
- [A title word literally equal to `--tag` cannot be stored] → Same limitation every flag-taking CLI has; acceptable for this tool.
- [Hand-rolled parsing can drift as more options are added] → Scope is a single option today; revisit `argparse` if a second option appears.
- [A store containing a malformed `tags` value (e.g. a string) written by hand] → Not defended against, consistent with the current lack of validation for `url`/`title`.

## Migration Plan

None required: the store change is additive and optional. Rollback is replacing `bm.py` with the previous version; tagged entries keep working there (tags are ignored).
