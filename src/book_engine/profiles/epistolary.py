from __future__ import annotations

from ..models import Book
from ..parsers.gutenberg_txt import parse_gutenberg_epistolary
from ..parsers.hyperion_txt import parse_hyperion_epistolary

SUPPORTED_SOURCE_FORMATS = {"gutenberg-txt", "plain-txt"}
SUPPORTED_PARSERS = {
    "gutenberg-letters-v1": parse_gutenberg_epistolary,
    "hyperion-letters-v1": parse_hyperion_epistolary,
}


def build_book_sections(book: Book) -> Book:
    source_path = book.root / book.config.source_file
    if book.config.source_format not in SUPPORTED_SOURCE_FORMATS:
        raise ValueError(f"Unsupported source format: {book.config.source_format}")
    try:
        parser = SUPPORTED_PARSERS[book.config.parser]
    except KeyError as exc:
        raise ValueError(f"Unsupported parser: {book.config.parser}") from exc
    book.sections = parser(source_path, book.config.title, source_format=book.config.source_format)
    return book
