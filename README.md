# book-engine

`book-engine` is a static site generator for books-as-websites.

It is built around a clean split between:
- **engine repo**: parsing, normalization, rendering, validation, build CLI
- **content repo**: raw source texts, metadata, themes, and per-book configuration

## Supported profiles

- `epistolary` — one HTML page per letter/document with sequential navigation
- `chaptered` — one HTML page per chapter with a generated table of contents

Both profiles currently support `gutenberg-txt` inputs.
The `epistolary` parser now handles these Gutenberg heading patterns:
- Roman-numeral sections with italic `_From ... to ..._` correspondent lines
- direct `To ...` letter headers
- Clarissa-style `LETTER I` headings followed by an uppercase correspondent line containing ` TO `
- Pamela-style `LETTER I` headings followed by an uppercase salutation line, optionally after a bracketed continuation note

The `chaptered` parser now handles both of these Gutenberg heading patterns:
- `CHAPTER I` followed by a title on the next non-blank line
- `CHAPTER I. Inline title text` with wrapped title lines before the first blank line
- top-level `BOOK I` / `BOOK II.` divisions, including Werther-style editorial codas like `THE EDITOR TO THE READER.`

## Local development

### Install editable package

```bash
pip install -e .
```

### Run tests

```bash
python -m pytest -q
```

### Build a content repo

```bash
book-engine build ../epistolary-library --output ../epistolary-library/dist
```

If `pip` is unavailable locally, a development fallback is:

```bash
PYTHONPATH='C:/Users/executor/Documents/book-engine/src' python -m book_engine.cli build ../epistolary-library --output ../epistolary-library/dist
```

## Repo roles

- `book-engine`: reusable compiler/runtime
- `epistolary-library`: reference content source of truth

## GitHub Actions

This repo includes CI at `.github/workflows/ci.yml`.
It:
- installs Python 3.11
- installs the package in editable mode
- runs the test suite

## Git identity hygiene

This repo includes a `.mailmap` so historical commits with the old `cduffy@ranchcryogenics.com` author email are normalized to `spinchange@gmail.com` in tools that honor mailmap.

To pin the repo-local author identity for future commits:

```bash
git config user.name 'Chris Duffy'
git config user.email 'spinchange@gmail.com'
```
