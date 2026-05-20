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
```

## Profile-specific expectations

### `epistolary`

Recommended parser metadata:

```yaml
profile: epistolary
parser: gutenberg-letters-v1
```

Expected source structure:
- Project Gutenberg header/footer markers
- section headings as Roman numerals (`I`, `II`, ...)
- a following italicized sender/recipient line such as `_From A. to B._`
- optional short dateline paragraph used as subtitle

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
- Project Gutenberg header/footer markers
- chapter headings like `CHAPTER I`, `CHAPTER II`, or `CHAPTER 3`
- optional chapter title on the next non-blank line
- or inline Gutenberg headings like `CHAPTER I. A Stormy Beginning`, including wrapped continuation lines before the first blank line
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
