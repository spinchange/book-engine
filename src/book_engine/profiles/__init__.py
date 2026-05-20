from __future__ import annotations

from collections.abc import Callable

from ..models import Book
from .chaptered import build_book_sections as build_chaptered_book
from .epistolary import build_book_sections as build_epistolary_book

PROFILE_BUILDERS: dict[str, Callable[[Book], Book]] = {
    "chaptered": build_chaptered_book,
    "epistolary": build_epistolary_book,
}


def build_sections_for_profile(book: Book) -> Book:
    try:
        builder = PROFILE_BUILDERS[book.config.profile]
    except KeyError as exc:
        raise ValueError(f"Unsupported profile: {book.config.profile}") from exc
    return builder(book)
