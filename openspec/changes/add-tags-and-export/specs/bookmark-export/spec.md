# Spec Delta

## Purpose

Lets users take their bookmarks out of `bm` as a Netscape bookmarks HTML file, the de-facto interchange format that browsers and bookmark managers import.

## ADDED Requirements

### Requirement: Export command destination
`bm export` SHALL write the export document to stdout. `bm export <path>` SHALL write it to `<path>` as UTF-8, creating or overwriting the file, and print nothing to stdout. More than one argument SHALL be rejected with an error on stderr and exit code 2.

#### Scenario: Export to stdout
- **WHEN** the user runs `bm export`
- **THEN** the export document is printed to stdout and the exit code is 0

#### Scenario: Export to a file
- **WHEN** the user runs `bm export bookmarks.html`
- **THEN** `bookmarks.html` contains the export document, nothing is printed to stdout, and the exit code is 0

#### Scenario: Too many arguments
- **WHEN** the user runs `bm export a.html b.html`
- **THEN** an error is printed to stderr, the exit code is 2, and no file is written

#### Scenario: Unwritable destination
- **WHEN** the user runs `bm export /nonexistent-dir/bookmarks.html`
- **THEN** an error naming the path is printed to stderr, no traceback is shown, and the exit code is 1

### Requirement: Netscape bookmark document structure
The export SHALL be a Netscape bookmarks document: it SHALL start with `<!DOCTYPE NETSCAPE-Bookmark-file-1>`, declare `charset=UTF-8` in a `<META HTTP-EQUIV="Content-Type">` element, contain `<TITLE>Bookmarks</TITLE>` and `<H1>Bookmarks</H1>`, and list bookmarks inside a single `<DL><p>` … `</DL><p>` block with no folders.

#### Scenario: Document skeleton
- **WHEN** the user exports any collection
- **THEN** the first line is `<!DOCTYPE NETSCAPE-Bookmark-file-1>` and the document contains the META charset, TITLE, H1 and one DL block

#### Scenario: Empty collection
- **WHEN** the store is empty or `~/.bm.json` does not exist and the user runs `bm export`
- **THEN** a complete document with an empty DL block is produced and the exit code is 0

### Requirement: One entry per bookmark
Each bookmark SHALL appear as one `<DT><A HREF="<url>">title</A>` line, in the same order as `bm list`. When the bookmark has tags, the `A` element SHALL carry a `TAGS` attribute holding the tags joined by commas without spaces; untagged bookmarks SHALL have no `TAGS` attribute.

#### Scenario: Tagged and untagged bookmarks
- **WHEN** the store holds `Example <https://example.com>` with no tags followed by `Python <https://python.org>` tagged `lang`, `docs`, and the user runs `bm export`
- **THEN** the DL block contains `<DT><A HREF="https://example.com">Example</A>` followed by `<DT><A HREF="https://python.org" TAGS="lang,docs">Python</A>`

#### Scenario: Pre-existing store without tags
- **WHEN** `~/.bm.json` contains only entries without a `tags` field and the user runs `bm export`
- **THEN** every entry is exported without a `TAGS` attribute and the store file is unchanged

### Requirement: HTML escaping
URLs, titles and tags SHALL be HTML-escaped in the export so that `&`, `<`, `>` and `"` cannot break the document structure; non-ASCII characters SHALL be emitted as UTF-8 text.

#### Scenario: Special characters in title and URL
- **WHEN** a bookmark has URL `https://example.com/?a=1&b="2"` and title `<Tom & Jerry>`, and the user runs `bm export`
- **THEN** its entry is `<DT><A HREF="https://example.com/?a=1&amp;b=&quot;2&quot;">&lt;Tom &amp; Jerry&gt;</A>`

#### Scenario: Non-ASCII title
- **WHEN** a bookmark has title `Café` and the user exports to a file
- **THEN** the file contains `Café` encoded as UTF-8
