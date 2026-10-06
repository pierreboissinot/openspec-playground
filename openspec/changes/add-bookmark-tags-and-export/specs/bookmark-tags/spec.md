# Spec Delta

## Purpose

Lets users group bookmarks with free-form tags, see those tags, and narrow the bookmark list to a tag, without breaking bookmark files created before tags existed.

## ADDED Requirements

### Requirement: Tag bookmarks on add
`bm add` SHALL accept zero or more `--tag <name>` options anywhere after the URL and store the given tags on the new bookmark. Arguments that are not `--tag` options or their values SHALL keep forming the title as they do today.

#### Scenario: Add with several tags
- **WHEN** the user runs `bm add https://example.com Example Site --tag dev --tag docs`
- **THEN** a bookmark is stored with URL `https://example.com`, title `Example Site` and tags `dev`, `docs`

#### Scenario: Tag option before the title
- **WHEN** the user runs `bm add https://example.com --tag dev Example`
- **THEN** a bookmark is stored with title `Example` and tag `dev`

#### Scenario: Add without tags
- **WHEN** the user runs `bm add https://example.com Example`
- **THEN** a bookmark is stored with no tags, exactly as before this change

#### Scenario: Tags only, no title
- **WHEN** the user runs `bm add https://example.com --tag dev`
- **THEN** a bookmark is stored with the URL as its title and tag `dev`

### Requirement: Tag normalization
Tags SHALL be trimmed and lowercased. Duplicate tags on the same bookmark SHALL be stored only once, in the order they first appear.

#### Scenario: Mixed case and duplicates
- **WHEN** the user runs `bm add https://example.com --tag Dev --tag dev --tag " DOCS "`
- **THEN** the bookmark is stored with tags `dev`, `docs`, in that order

### Requirement: Invalid tag rejection
`bm add` SHALL reject a `--tag` option that has no value, or whose value is empty after trimming or contains whitespace or a comma. It SHALL print an error to stderr, exit with status 2, and leave the bookmark file unchanged.

#### Scenario: Missing tag value
- **WHEN** the user runs `bm add https://example.com --tag`
- **THEN** an error is printed to stderr, the exit status is 2, and no bookmark is added

#### Scenario: Tag containing a comma
- **WHEN** the user runs `bm add https://example.com --tag a,b`
- **THEN** an error is printed to stderr, the exit status is 2, and no bookmark is added

### Requirement: Show tags in list
`bm list` SHALL append each tag of a bookmark to its line as ` #<tag>`, in stored order. The line of a bookmark without tags SHALL stay unchanged: `<n>. <title> <<url>>`.

#### Scenario: Tagged bookmark line
- **WHEN** bookmark 1 has title `Example`, URL `https://example.com` and tags `dev`, `docs`, and the user runs `bm list`
- **THEN** the output line is `1. Example <https://example.com> #dev #docs`

#### Scenario: Untagged bookmark line
- **WHEN** bookmark 1 has title `Example`, URL `https://example.com` and no tags, and the user runs `bm list`
- **THEN** the output line is `1. Example <https://example.com>`

### Requirement: Filter list by tag
`bm list` SHALL accept zero or more `--tag <name>` options, normalized like tags on add. When given, it SHALL show only bookmarks that carry every given tag. Each shown bookmark SHALL keep its position number from the unfiltered list.

#### Scenario: Filter by one tag
- **WHEN** bookmarks 1 (`dev`), 2 (no tags) and 3 (`dev`, `docs`) exist and the user runs `bm list --tag dev`
- **THEN** only bookmarks 1 and 3 are shown, numbered `1.` and `3.`

#### Scenario: Filter by several tags
- **WHEN** bookmarks 1 (`dev`) and 3 (`dev`, `docs`) exist and the user runs `bm list --tag dev --tag docs`
- **THEN** only bookmark 3 is shown, numbered `3.`

#### Scenario: Filter is case-insensitive
- **WHEN** bookmark 1 has tag `dev` and the user runs `bm list --tag DEV`
- **THEN** bookmark 1 is shown

#### Scenario: No match
- **WHEN** no bookmark has tag `missing` and the user runs `bm list --tag missing`
- **THEN** nothing is printed and the exit status is 0

#### Scenario: Remove by filtered position
- **WHEN** `bm list --tag docs` shows `3. Docs <https://docs.example>` and the user runs `bm rm 3`
- **THEN** the bookmark `https://docs.example` is removed

### Requirement: Legacy bookmark files remain usable
Bookmark files written before tags existed, whose entries have no `tags` field, SHALL load without error. Their bookmarks SHALL be treated as untagged by every command. Untagged bookmarks SHALL be stored without a `tags` field.

#### Scenario: List a legacy file
- **WHEN** `~/.bm.json` contains `[{"url": "https://example.com", "title": "Example"}]` and the user runs `bm list`
- **THEN** the output is `1. Example <https://example.com>` and the exit status is 0

#### Scenario: Add to a legacy file
- **WHEN** `~/.bm.json` contains a legacy entry and the user runs `bm add https://new.example --tag dev`
- **THEN** the file contains the legacy entry unchanged, with no `tags` field, followed by the new entry with `"tags": ["dev"]`

#### Scenario: Filter a legacy file
- **WHEN** `~/.bm.json` contains only legacy entries and the user runs `bm list --tag dev`
- **THEN** nothing is printed and the exit status is 0
