# Content Schema

## `library.yaml`

```yaml
title: Epistolary Library
description: HTML editions of public-domain and demo books
base_url: ""
books_dir: books
output_dir: dist
default_theme: classic-paper
```

## `book.yaml`

```yaml
id: lady-susan
title: Lady Susan
author: Jane Austen
year: 1871
source_file: source.txt
source_format: gutenberg-txt
profile: epistolary
parser: gutenberg-letters-v1
theme: regency-paper
source_url: https://www.gutenberg.org/cache/epub/946/pg946.txt
description: Jane Austen's epistolary novella rendered as linked HTML pages.
front_matter:
  - id: translators-note
    title: Translator's Note
    source_file: translator-note.md
    source_format: markdown
```

## Profile-specific expectations

## Optional `front_matter`

A book can now define optional front-matter pages that are rendered before the main section sequence.

Each entry currently supports:
- `id` — output filename stem (for example `translators-note` → `translators-note.html`)
- `title` — page title and TOC label
- `source_file` — local file under the book directory
- `source_format` — currently `markdown` (default) or `plain-txt`

Behavior:
- front matter pages appear in the book TOC before Letter I / Chapter I
- prev/next navigation includes front matter pages in sequence
- markdown sources strip an opening matching `# Heading` line when it duplicates the configured title
- markdown currently supports paragraph blocks, second-level headings, unordered lists, emphasis, and inline code

### `source_format`

- `gutenberg-txt`
  - expects Project Gutenberg start/end markers
  - strips wrapper text before handing content to the profile parser
- `plain-txt`
  - treats the whole file as already-normalized body text
  - makes no Project Gutenberg marker assumptions
  - still relies on the selected profile's heading grammar (`epistolary`, `chaptered`, etc.)

### `epistolary`

Recommended parser metadata:

```yaml
profile: epistolary
parser: gutenberg-letters-v1
```

Alternate parser for Hyperion-style plain texts:

```yaml
profile: epistolary
source_format: plain-txt
parser: hyperion-letters-v1
```

Expected source structure:
- either Project Gutenberg header/footer markers (`gutenberg-txt`) or already-normalized plain text (`plain-txt`)
- one of these heading grammars:
  - section headings as Roman numerals (`I`, `II`, ...`) with a following italicized sender/recipient line such as `_From A. to B._`
  - section headings as Roman numerals (`I`, `II`, ...`) with an uppercase correspondent line such as `FROM DANE KEMPTON TO HERBERT WACE`, followed by location/date metadata lines
  - section headings as Roman numerals (`I`, `II`, ...`) with a dateline paragraph followed by an italicized salutation paragraph such as `_Dear Pierrepont:_ ...`
  - direct `To ...` letter headers followed by the salutation/body
  - standalone `LETTER I`, `LETTER II`, etc. followed by an uppercase correspondent line containing ` TO `
  - standalone `LETTER I`, `LETTER II`, etc. followed by an uppercase salutation line such as `DEAR FATHER AND MOTHER,`, optionally with a bracketed continuation note like `[In answer to the preceding.]`
  - standalone `LETTER I`, `LETTER II`, etc. that inherit a nearby global `FROM ... TO ...` correspondent title block
- optional short dateline paragraph used as subtitle

Additional supported epistolary parser variant:
- `hyperion-letters-v1`
  - intended for `plain-txt`
  - expects correspondent headings like `Hyperion to Bellarmin [I]`
  - uses the bracketed Roman numeral as the section label/id basis

Output shape:
- one page per letter/document
- generated TOC
- sequential prev/next navigation

### `chaptered`

Recommended parser metadata:

```yaml
profile: chaptered
parser: gutenberg-chapters-v1
```

Expected source structure:
- either Project Gutenberg header/footer markers (`gutenberg-txt`) or already-normalized plain text (`plain-txt`)
- chapter headings like `CHAPTER I`, `CHAPTER II`, or `CHAPTER 3`
- optional chapter title on the next non-blank line
- or inline Gutenberg headings like `CHAPTER I. A Stormy Beginning`, including wrapped continuation lines before the first blank line
- or French `CHAPITRE PREMIER` / `CHAPITRE II` headings
- or top-level `BOOK I` / `BOOK II.` divisions when a work is structurally part-based rather than chapter-based
- optional editorial coda headings like `THE EDITOR TO THE READER.` when they function as the final top-level section
- optional appendix headings like `LETTRE À L'ÉDITEUR` and `RÉPONSE.`
- body paragraphs separated by blank lines

Output shape:
- one page per chapter
- generated TOC
- sequential prev/next navigation

## Conceptual model

- **Library**: top-level collection and output settings
- **Book**: one text plus metadata and profile selection
- **Profile**: content grammar (`epistolary`, `chaptered`, later `diary`, `mixed-documents`)
- **Parser**: transforms raw source text into normalized sections
- **Renderer**: turns normalized sections into HTML pages
