# book-engine

`book-engine` is a static site generator for books-as-websites.

It is built around a clean split between:
- **engine repo**: parsing, normalization, rendering, validation, build CLI
- **content repo**: raw source texts, metadata, themes, and per-book configuration

## Supported profiles

- `epistolary` — one HTML page per letter/document with sequential navigation
- `chaptered` — one HTML page per chapter with a generated table of contents

Both profiles currently support `gutenberg-txt` inputs.

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
