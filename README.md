# book-engine

`book-engine` is a static site generator for books-as-websites.

It is built around a clean split between:
- **engine repo**: parsing, normalization, rendering, validation, build CLI
- **content repo**: raw source texts, metadata, themes, and per-book configuration

## Supported profiles

- `epistolary` — one HTML page per letter/document with sequential navigation
- `chaptered` — one HTML page per chapter with a generated table of contents

Both profiles currently support these source formats:
- `gutenberg-txt` — Project Gutenberg plain text with wrapper markers that should be stripped before parsing
- `plain-txt` — already-normalized plain text with no Gutenberg wrapper assumptions

The `epistolary` parser now handles these Gutenberg heading patterns:
- Roman-numeral sections with italic `_From ... to ..._` correspondent lines
- Roman-numeral sections with a dateline followed by an italicized salutation paragraph like `_Dear Pierrepont:_ ...`
- direct `To ...` letter headers
- Clarissa-style `LETTER I` headings followed by an uppercase correspondent line containing ` TO `
- Pamela-style `LETTER I` headings followed by an uppercase salutation line, optionally after a bracketed continuation note
- Portuguese-Nun-style `LETTER I` headings that inherit a nearby global `FROM ... TO ...` correspondent title

`plain-txt` currently reuses the same section-heading grammars as `gutenberg-txt`; it only changes source extraction by treating the whole file as the parseable body.

Available epistolary parser variants:
- `gutenberg-letters-v1` — default Gutenberg-oriented epistolary grammar
- `hyperion-letters-v1` — plain-text Hyperion-style headings like `Hyperion to Bellarmin [I]`

The `chaptered` parser now handles both of these Gutenberg heading patterns:
- `CHAPTER I` followed by a title on the next non-blank line
- `CHAPTER I. Inline title text` with wrapped title lines before the first blank line
- French `CHAPITRE PREMIER` / `CHAPITRE II` headings, including appendix-style `LETTRE À L'ÉDITEUR` and `RÉPONSE.` sections
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
