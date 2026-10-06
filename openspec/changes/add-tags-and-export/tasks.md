# Tasks

## 1. Test harness and compatibility baseline

- [ ] 1.1 Create `test_bm.py` (stdlib `unittest`) with a fixture that points `bm.STORE` at a temporary file and captures stdout/stderr from `bm.main()`; verify `python -m unittest` discovers and runs it
- [ ] 1.2 Add baseline tests for current behaviour on a legacy store (`[{"url": ..., "title": ...}]`): `list` output format, no-argument `list`, `add` appends, `rm` removes, unknown command exits 2; verify they pass against the unmodified `bm.py` and that `list` leaves the file bytes unchanged

## 2. Tags on add and list

- [ ] 2.1 Implement the `--tag` extraction helper (`--tag NAME` and `--tag=NAME`, any position; strip, lowercase, de-duplicate in first-seen order; usage error on missing value, empty tag, or comma) and the `main()` handling that prints the error to stderr and returns 2; verify with unit tests for each normalization and rejection case in `specs/bookmark-tags` ("Tag normalization", "Reject invalid tag arguments")
- [ ] 2.2 Make `add` use the helper, store `tags` only when non-empty, and reject `add` with no URL left after option extraction (exit 2, store untouched); verify tests for the "Tag a bookmark when adding it" scenarios, the "Add with tags but no URL" scenario, and that an untagged add writes an entry with only `url` and `title`
- [ ] 2.3 Make `list` print ` [tag, tag]` after the URL for tagged bookmarks, read tags via `.get("tags", [])`, and filter by all given `--tag` values while keeping original numbering; verify tests for "Show tags in the listing", "Filter the listing by tag", "Filtered listing keeps original numbers" (including `rm` on the shown number) and the "Backward-compatible bookmark store" scenarios; confirm the group 1 baseline tests still pass
- [ ] 2.4 Document `--tag` on `add` and `list` in `README.md`, including lowercasing and AND semantics of repeated filters; verify each documented command runs as written against a temporary `HOME`

## 3. Netscape HTML export

- [ ] 3.1 Implement the pure rendering function that turns the bookmark list into the Netscape document (DOCTYPE, META charset, TITLE, H1, single `<DL><p>` block, one `<DT><A HREF=...>` line per bookmark, `TAGS="a,b"` only when tagged, `html.escape(quote=True)` on URL, title and tags); verify unit tests for "Netscape bookmark document structure", "One entry per bookmark" and "HTML escaping" (exact expected lines from the spec)
- [ ] 3.2 Add the `export` command: no argument writes UTF-8 bytes to `sys.stdout.buffer`, one argument writes the file with `encoding="utf-8"`, more than one argument exits 2, `OSError` prints `bm: cannot write <path>: <reason>` and exits 1; verify tests for every "Export command destination" scenario, the empty/missing store case, and a legacy store export leaving `~/.bm.json` unchanged — the stdout case run as a subprocess with `HOME` set to a temporary directory
- [ ] 3.3 Document `bm export [PATH]` in `README.md`; verify the documented command produces a file whose first line is `<!DOCTYPE NETSCAPE-Bookmark-file-1>`

## 4. Integration check

- [ ] 4.1 Copy a legacy-format `~/.bm.json` into a temporary `HOME`, then run `add --tag`, `list`, `list --tag`, `rm`, and `export` end to end via `python bm.py`; verify outputs match the specs, the full `python -m unittest` suite passes, and the resulting store still lists correctly with the original (pre-change) `bm.py` from git
