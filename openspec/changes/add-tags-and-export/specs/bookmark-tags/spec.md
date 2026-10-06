# Spec Delta

## Purpose

Lets users label bookmarks with free-form tags and narrow the bookmark listing to a tag, while keeping bookmark stores created before tags existed fully usable.

## ADDED Requirements

### Requirement: Tag a bookmark when adding it
`bm add` SHALL accept zero or more `--tag <name>` options (also written `--tag=<name>`), placed anywhere after `add`, and SHALL store the given tags with the new bookmark. Arguments that are not `--tag` options or their values SHALL keep their current meaning: the first is the URL, the rest form the title.

#### Scenario: Add with a single tag
- **WHEN** the user runs `bm add https://example.com Example --tag docs`
- **THEN** a bookmark with URL `https://example.com`, title `Example` and tags `docs` is stored

#### Scenario: Add with several tags in any position
- **WHEN** the user runs `bm add --tag python https://docs.python.org Python docs --tag=reference`
- **THEN** a bookmark with URL `https://docs.python.org`, title `Python docs` and tags `python`, `reference` is stored

#### Scenario: Add without tags
- **WHEN** the user runs `bm add https://example.com Example`
- **THEN** a bookmark with no tags is stored and the command behaves as before this change

### Requirement: Tag normalization
Tags SHALL be stored trimmed of surrounding whitespace and lowercased. Duplicate tags on the same bookmark SHALL be stored once, keeping the order of first occurrence.

#### Scenario: Mixed-case and duplicate tags
- **WHEN** the user runs `bm add https://example.com --tag Docs --tag docs --tag " Web "`
- **THEN** the stored bookmark has exactly the tags `docs`, `web`, in that order

### Requirement: Reject invalid tag arguments
The CLI SHALL reject a `--tag` option with no value, a tag that is empty after trimming, or a tag containing a comma, by printing an error to stderr and exiting with code 2 without modifying the bookmark store.

#### Scenario: Missing tag value
- **WHEN** the user runs `bm add https://example.com --tag`
- **THEN** an error is printed to stderr, the exit code is 2, and no bookmark is added

#### Scenario: Tag containing a comma
- **WHEN** the user runs `bm add https://example.com --tag a,b`
- **THEN** an error is printed to stderr, the exit code is 2, and no bookmark is added

#### Scenario: Add with tags but no URL
- **WHEN** the user runs `bm add --tag docs`
- **THEN** an error is printed to stderr, the exit code is 2, and no bookmark is added

### Requirement: Show tags in the listing
`bm list` SHALL print each tagged bookmark as `<n>. <title> <<url>> [<tag>, <tag>, ...]`. Bookmarks without tags SHALL print exactly as before this change: `<n>. <title> <<url>>`.

#### Scenario: Listing a tagged and an untagged bookmark
- **WHEN** the store holds `Example <https://example.com>` with no tags followed by `Python <https://python.org>` tagged `lang`, `docs`, and the user runs `bm list`
- **THEN** the output is `1. Example <https://example.com>` then `2. Python <https://python.org> [lang, docs]`

### Requirement: Filter the listing by tag
`bm list` SHALL accept zero or more `--tag <name>` options (also `--tag=<name>`). When at least one is given, only bookmarks carrying every given tag SHALL be printed. Filter values SHALL be normalized like stored tags before matching. Invalid filter values SHALL be rejected as for `add`.

#### Scenario: Filter by one tag
- **WHEN** the store holds bookmarks tagged `docs`, `news`, and `docs` respectively, and the user runs `bm list --tag docs`
- **THEN** only the first and third bookmarks are printed

#### Scenario: Filter by several tags
- **WHEN** the user runs `bm list --tag python --tag docs`
- **THEN** only bookmarks tagged with both `python` and `docs` are printed

#### Scenario: Filter is case-insensitive
- **WHEN** a bookmark is tagged `docs` and the user runs `bm list --tag DOCS`
- **THEN** that bookmark is printed

#### Scenario: No bookmark matches
- **WHEN** no bookmark carries the tag `missing` and the user runs `bm list --tag missing`
- **THEN** nothing is printed and the exit code is 0

### Requirement: Filtered listing keeps original numbers
A filtered `bm list` SHALL number each printed bookmark with its position in the full collection, so that the number can be passed to `bm rm`.

#### Scenario: Number matches the unfiltered position
- **WHEN** the store holds three bookmarks and only the third is tagged `docs`, and the user runs `bm list --tag docs`
- **THEN** the single printed line starts with `3.`, and `bm rm 3` removes that bookmark

### Requirement: Backward-compatible bookmark store
Bookmark entries in `~/.bm.json` that have no `tags` field SHALL be treated as having no tags. Reading such a store SHALL NOT fail or require a migration, and commands that do not modify the store SHALL NOT rewrite it. A store written by this version SHALL keep each entry's `url` and `title` fields unchanged in name and meaning.

#### Scenario: Pre-existing store is listed
- **WHEN** `~/.bm.json` contains `[{"url": "https://example.com", "title": "Example"}]` and the user runs `bm list`
- **THEN** the output is `1. Example <https://example.com>` and the file content is unchanged

#### Scenario: Pre-existing store is filtered
- **WHEN** `~/.bm.json` contains only entries without a `tags` field and the user runs `bm list --tag docs`
- **THEN** nothing is printed and the exit code is 0

#### Scenario: Adding to a pre-existing store
- **WHEN** `~/.bm.json` contains entries without a `tags` field and the user runs `bm add https://new.example --tag news`
- **THEN** the existing entries are preserved with their `url` and `title`, and the new entry is appended with tag `news`

#### Scenario: Removing from a pre-existing store
- **WHEN** `~/.bm.json` contains two entries without a `tags` field and the user runs `bm rm 1`
- **THEN** only the second entry remains, with its `url` and `title` intact
