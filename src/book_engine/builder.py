from __future__ import annotations

from pathlib import Path

from .config import load_book_config, load_library_config
from .front_matter import build_front_matter_sections
from .models import Book
from .profiles import build_sections_for_profile
from .renderers.html import render_book, render_library_index


def build_library(content_root: Path, output_override: Path | None = None) -> Path:
    content_root = content_root.resolve()
    library = load_library_config(content_root)
    output_dir = output_override.resolve() if output_override else (content_root / library["output_dir"]).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    books_dir = content_root / library["books_dir"]
    books: list[Book] = []
    for book_yaml in sorted(books_dir.glob("*/book.yaml")):
        config = load_book_config(book_yaml)
        book = Book(config=config, root=book_yaml.parent)
        built_book = build_sections_for_profile(book)
        front_matter = build_front_matter_sections(built_book)
        if front_matter:
            built_book.sections = front_matter + built_book.sections
            for order, section in enumerate(built_book.sections, start=1):
                section.order = order
        books.append(built_book)

    render_library_index(library, books, output_dir)
    for book in books:
        render_book(book, output_dir)
    return output_dir
