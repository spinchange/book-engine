from __future__ import annotations

from ..models import Book
from ..parsers.gutenberg_txt import parse_gutenberg_epistolary


def build_book_sections(book: Book) -> Book:
    source_path = book.root / book.config.source_file
    if book.config.source_format != "gutenberg-txt":
        raise ValueError(f"Unsupported source format: {book.config.source_format}")
    book.sections = parse_gutenberg_epistolary(source_path, book.config.title)
    return book
