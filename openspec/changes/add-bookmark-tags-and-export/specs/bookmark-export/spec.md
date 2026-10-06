# Spec Delta

## Purpose

Lets users take their bookmarks out of `bm` as a Netscape bookmarks HTML file, the interchange format that mainstream browsers and bookmark services import.

## ADDED Requirements

### Requirement: Export command
`bm export` SHALL write all stored bookmarks, in stored order, as one Netscape bookmarks HTML document. With no argument it SHALL write to stdout. With one path argument it SHALL create or overwrite that file and print nothing to stdout. It SHALL exit with status 0 on success.

#### Scenario: Export to stdout
- **WHEN** two bookmarks exist and the user runs `bm export`
- **THEN** a Netscape bookmarks document containing both bookmarks, in stored order, is written to stdout and the exit status is 0

#### Scenario: Export to a file
- **WHEN** the user runs `bm export bookmarks.html`
- **THEN** `bookmarks.html` contains the document, nothing is printed to stdout, and the exit status is 0

#### Scenario: Overwrite an existing file
- **WHEN** `bookmarks.html` already exists and the user runs `bm export bookmarks.html`
- **THEN** its previous content is replaced by the exported document

#### Scenario: Bookmark file is not modified
- **WHEN** the user runs `bm export`
- **THEN** `~/.bm.json` is left unchanged

### Requirement: Netscape document structure
The document SHALL be UTF-8 encoded. It SHALL start with `<!DOCTYPE NETSCAPE-Bookmark-file-1>`, then a `<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">` line, `<TITLE>Bookmarks</TITLE>` and `<H1>Bookmarks</H1>`. These SHALL be followed by a `<DL><p>` list holding one `<DT><A HREF="<url>">` entry per bookmark, whose link text is the bookmark title. The list SHALL close with `</DL><p>`.

#### Scenario: Single bookmark
- **WHEN** the only bookmark has URL `https://example.com` and title `Example` and no tags, and the user runs `bm export`
- **THEN** the output contains the header lines above and exactly one entry `<DT><A HREF="https://example.com">Example</A>` inside the `<DL><p>` … `</DL><p>` list

#### Scenario: Empty bookmark store
- **WHEN** no bookmarks exist (or `~/.bm.json` does not exist) and the user runs `bm export`
- **THEN** a valid document with the header lines and an empty `<DL><p>` … `</DL><p>` list is written and the exit status is 0

#### Scenario: Non-ASCII title
- **WHEN** a bookmark title is `Café`
- **THEN** the exported entry contains `Café` encoded as UTF-8

### Requirement: Tags in export
An exported entry for a bookmark with tags SHALL carry a `TAGS` attribute on its `<A>` element, holding the tags in stored order and joined by commas with no spaces. Entries for untagged bookmarks SHALL have no `TAGS` attribute.

#### Scenario: Tagged bookmark
- **WHEN** a bookmark with URL `https://example.com`, title `Example` and tags `dev`, `docs` is exported
- **THEN** its entry is `<DT><A HREF="https://example.com" TAGS="dev,docs">Example</A>`

#### Scenario: Legacy bookmark
- **WHEN** a bookmark loaded from a file written before tags existed is exported
- **THEN** its entry has no `TAGS` attribute

### Requirement: HTML escaping
Exported URLs, titles and tags SHALL be HTML-escaped so that `&`, `<`, `>` and `"` cannot break the document structure.

#### Scenario: Special characters in title and URL
- **WHEN** a bookmark has URL `https://example.com/?a=1&b="2"` and title `<Tom & Jerry>`
- **THEN** its entry is `<DT><A HREF="https://example.com/?a=1&amp;b=&quot;2&quot;">&lt;Tom &amp; Jerry&gt;</A>`

### Requirement: Export write failure
If the output file cannot be written, `bm export <path>` SHALL print an error naming the path to stderr and exit with status 1, without a Python traceback.

#### Scenario: Unwritable path
- **WHEN** the user runs `bm export /nonexistent-dir/bookmarks.html`
- **THEN** an error mentioning `/nonexistent-dir/bookmarks.html` is printed to stderr, no traceback is shown, and the exit status is 1
