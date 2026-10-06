# Tasks

## 1. Test harness

- [ ] 1.1 Create `test_bm.py` with a `unittest.TestCase` base that redirects `bm.STORE` to a temp file and captures stdout/stderr per [D6](./design.md#d6-stdlib-unittest-driving-main); add baseline tests for current `add`/`list`/`rm` and unknown-command (exit 2) behavior, and verify `python -m unittest -v` passes against the unchanged `bm.py`

## 2. Tags on add and legacy compatibility

- [ ] 2.1 Add the `--tag` extraction helper per [D2](./design.md#d2-hand-rolled---tag-extraction-instead-of-argparse) and the normalization/validation per [D3](./design.md#d3-tag-normalization-rules); verify with tests for the "Tag normalization" and "Invalid tag rejection" scenarios (including file unchanged on error)
- [ ] 2.2 Store tags on `add` using the optional field per [D1](./design.md#d1-optional-tags-field-no-schema-version); verify with tests for every "Tag bookmarks on add" scenario
- [ ] 2.3 Verify the "Legacy bookmark files remain usable" scenarios with tests that seed a tag-less JSON file, then `list`, `add --tag` and assert the legacy entry is written back without a `tags` key

## 3. Tags in list

- [ ] 3.1 Render ` #<tag>` suffixes in `list` output; verify with tests for both "Show tags in list" scenarios (untagged line byte-identical to before)
- [ ] 3.2 Implement `list --tag` AND filtering with full-list numbering per [D4](./design.md#d4-and-filtering-with-stable-numbering); verify with tests for every "Filter list by tag" scenario, including `rm` by a filtered position
- [ ] 3.3 Document `--tag` on `add` and `list` in `README.md`; verify the documented commands run as written against a scratch `HOME`

## 4. Export

- [ ] 4.1 Implement the Netscape document renderer per [D5](./design.md#d5-export-rendering); verify with tests for the "Netscape document structure", "Tags in export" and "HTML escaping" scenarios
- [ ] 4.2 Wire the `export [path]` command (stdout default, file overwrite, `OSError` → stderr + exit 1); verify with tests for every "Export command" and "Export write failure" scenario, including `~/.bm.json` unchanged
- [ ] 4.3 Document `export` in `README.md`; verify `python bm.py export > /tmp/bm.html` produces a file that opens in a browser and imports into Firefox via *Import Bookmarks from HTML*

## 5. Integration check

- [ ] 5.1 Run `python -m unittest -v` and `openspec validate add-bookmark-tags-and-export --strict`; verify both pass
