from __future__ import annotations

from ..models import Book
from ..parsers.chaptered_txt import parse_chaptered_text


def build_book_sections(book: Book) -> Book:
    source_path = book.root / book.config.source_file
    if book.config.source_format != "gutenberg-txt":
        raise ValueError(f"Unsupported source format: {book.config.source_format}")
    book.sections = parse_chaptered_text(source_path, book.config.title)
    return book
