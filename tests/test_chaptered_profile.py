from pathlib import Path

import pytest

from book_engine.builder import build_library
from book_engine.parsers.chaptered_txt import parse_chaptered_text


CHAPTERED_TEXT = """*** START OF THE PROJECT GUTENBERG EBOOK SAMPLE CHAPTERED BOOK ***

CHAPTER I
A Beginning

This is the first paragraph.

This is the second paragraph.

CHAPTER II
Another Turn

This is chapter two.

*** END OF THE PROJECT GUTENBERG EBOOK SAMPLE CHAPTERED BOOK ***
"""

INLINE_HEADING_TEXT = """*** START OF THE PROJECT GUTENBERG EBOOK THE ADVENTURES OF TOM SAWYER ***

CHAPTER I. Y-o-u-u Tom—Aunt Polly Decides Upon her Duty—Tom Practices
Music—The Challenge—A Private Entrance

“Tom!”

No answer.

CHAPTER II. Strong Temptations—Strategic Movements—The Innocents
Beguiled

Saturday morning was come.

*** END OF THE PROJECT GUTENBERG EBOOK THE ADVENTURES OF TOM SAWYER ***
"""

TOC_THEN_BODY_TEXT = """*** START OF THE PROJECT GUTENBERG EBOOK THE ADVENTURES OF TOM SAWYER ***

CHAPTER I. Y-o-u-u Tom—Aunt Polly Decides Upon her Duty—Tom Practices
Music—The Challenge—A Private Entrance
CHAPTER II. Strong Temptations—Strategic Movements—The Innocents
Beguiled

By and by, they drifted apart.

CHAPTER I

“Tom!”

No answer.

CHAPTER II

Saturday morning was come.

*** END OF THE PROJECT GUTENBERG EBOOK THE ADVENTURES OF TOM SAWYER ***
"""

TOC_WITH_SPARSE_WRAPPED_BODY_TEXT = """*** START OF THE PROJECT GUTENBERG EBOOK THE ADVENTURES OF TOM SAWYER ***

CHAPTER I. Y-o-u-u Tom—Aunt Polly Decides Upon her Duty—Tom Practices
Music—The Challenge—A Private Entrance
CHAPTER II. Strong Temptations—Strategic Movements—The Innocents
Beguiled

CHAPTER I


“Tom!”

No answer.


The old lady pulled her spectacles down and looked over them about the

room.


CHAPTER II

Saturday morning was come.

*** END OF THE PROJECT GUTENBERG EBOOK THE ADVENTURES OF TOM SAWYER ***
"""

WRAPPED_SYNOPSIS_TEXT = """*** START OF THE PROJECT GUTENBERG EBOOK THE DIARY OF A NOBODY ***

CHAPTER II




Tradesmen and the scraper still troublesome.  Gowing rather tiresome with

his complaints of the paint.  I make one of the best jokes of my life.

Delights of Gardening.  Mr. Stillbrook, Gowing, Cummings, and I have a

little misunderstanding.  Sarah makes me look a fool before Cummings.



APRIL 9.—Commenced the morning badly.

The butcher called.



APRIL 10.—Farmerson came round to attend to the scraper himself.

He seems a very civil fellow.

*** END OF THE PROJECT GUTENBERG EBOOK THE DIARY OF A NOBODY ***
"""


def test_parse_chaptered_text_splits_chapters_and_paragraphs(tmp_path: Path) -> None:
    source = tmp_path / "sample.txt"
    source.write_text(CHAPTERED_TEXT, encoding="utf-8")

    sections = parse_chaptered_text(source, "Sample Chaptered Book")

    assert [section.id for section in sections] == ["chapter-i", "chapter-ii"]
    assert [section.label for section in sections] == ["Chapter I", "Chapter II"]
    assert sections[0].title == "A Beginning"
    assert sections[0].body == ["This is the first paragraph.", "This is the second paragraph."]
    assert sections[1].title == "Another Turn"
    assert sections[1].body == ["This is chapter two."]


def test_parse_chaptered_text_supports_inline_gutenberg_chapter_headings(tmp_path: Path) -> None:
    source = tmp_path / "tom-sawyer-sample.txt"
    source.write_text(INLINE_HEADING_TEXT, encoding="utf-8")

    sections = parse_chaptered_text(source, "The Adventures of Tom Sawyer")

    assert [section.id for section in sections] == ["chapter-i", "chapter-ii"]
    assert sections[0].label == "Chapter I"
    assert sections[0].title == "Y-o-u-u Tom—Aunt Polly Decides Upon her Duty—Tom Practices Music—The Challenge—A Private Entrance"
    assert sections[0].body == ["“Tom!”", "No answer."]
    assert sections[1].title == "Strong Temptations—Strategic Movements—The Innocents Beguiled"
    assert sections[1].body == ["Saturday morning was come."]


def test_parse_chaptered_text_skips_table_of_contents_entries(tmp_path: Path) -> None:
    source = tmp_path / "tom-sawyer-with-toc.txt"
    source.write_text(TOC_THEN_BODY_TEXT, encoding="utf-8")

    sections = parse_chaptered_text(source, "The Adventures of Tom Sawyer")

    assert [section.id for section in sections] == ["chapter-i", "chapter-ii"]
    assert sections[0].title == "Y-o-u-u Tom—Aunt Polly Decides Upon her Duty—Tom Practices Music—The Challenge—A Private Entrance"
    assert sections[0].body == ["“Tom!”", "No answer."]
    assert sections[1].body == ["Saturday morning was come."]


def test_parse_chaptered_text_prefers_toc_title_over_sparse_body_probe(tmp_path: Path) -> None:
    source = tmp_path / "tom-sawyer-with-toc-and-sparse-body.txt"
    source.write_text(TOC_WITH_SPARSE_WRAPPED_BODY_TEXT, encoding="utf-8")

    sections = parse_chaptered_text(source, "The Adventures of Tom Sawyer")

    assert [section.id for section in sections] == ["chapter-i", "chapter-ii"]
    assert sections[0].title == "Y-o-u-u Tom—Aunt Polly Decides Upon her Duty—Tom Practices Music—The Challenge—A Private Entrance"
    assert sections[0].body == [
        "“Tom!” No answer.",
        "The old lady pulled her spectacles down and looked over them about the room.",
    ]
    assert sections[1].body == ["Saturday morning was come."]


def test_parse_chaptered_text_preserves_wrapped_authorial_synopsis(tmp_path: Path) -> None:
    source = tmp_path / "diary-of-a-nobody.txt"
    source.write_text(WRAPPED_SYNOPSIS_TEXT, encoding="utf-8")

    sections = parse_chaptered_text(source, "The Diary of a Nobody")

    assert [section.id for section in sections] == ["chapter-ii"]
    assert sections[0].title == (
        "Tradesmen and the scraper still troublesome. Gowing rather tiresome with "
        "his complaints of the paint. I make one of the best jokes of my life. "
        "Delights of Gardening. Mr. Stillbrook, Gowing, Cummings, and I have a "
        "little misunderstanding. Sarah makes me look a fool before Cummings."
    )
    assert sections[0].body == [
        "APRIL 9.—Commenced the morning badly. The butcher called.",
        "APRIL 10.—Farmerson came round to attend to the scraper himself. He seems a very civil fellow.",
    ]


def test_build_library_supports_chaptered_and_epistolary_books(tmp_path: Path) -> None:
    content_root = tmp_path / "library"
    books_dir = content_root / "books"
    chaptered_dir = books_dir / "sample-chaptered"
    epistolary_dir = books_dir / "sample-letters"
    chaptered_dir.mkdir(parents=True)
    epistolary_dir.mkdir(parents=True)

    (content_root / "library.yaml").write_text(
        """title: Mixed Library
books_dir: books
output_dir: dist
""",
        encoding="utf-8",
    )
    (chaptered_dir / "book.yaml").write_text(
        """id: sample-chaptered
title: Sample Chaptered Book
author: Test Author
year: \"1900\"
source_file: source.txt
source_format: gutenberg-txt
profile: chaptered
parser: gutenberg-chapters-v1
theme: classic-paper
""",
        encoding="utf-8",
    )
    (chaptered_dir / "source.txt").write_text(CHAPTERED_TEXT, encoding="utf-8")

    (epistolary_dir / "book.yaml").write_text(
        """id: sample-letters
title: Sample Letters
author: Test Author
year: \"1901\"
source_file: source.txt
source_format: gutenberg-txt
profile: epistolary
parser: gutenberg-letters-v1
theme: classic-paper
""",
        encoding="utf-8",
    )
    (epistolary_dir / "source.txt").write_text(
        """*** START OF THE PROJECT GUTENBERG EBOOK SAMPLE LETTERS ***

I
_From A. to B._

Bath, Monday.

My dear friend,

I write to you at once.

II
_From B. to A._

London, Tuesday.

Your letter reached me.

*** END OF THE PROJECT GUTENBERG EBOOK SAMPLE LETTERS ***
""",
        encoding="utf-8",
    )

    output_dir = build_library(content_root)

    assert (output_dir / "index.html").exists()
    assert (output_dir / "books" / "sample-chaptered" / "chapter-i.html").exists()
    assert (output_dir / "books" / "sample-chaptered" / "chapter-ii.html").exists()
    assert (output_dir / "books" / "sample-letters" / "letter-i.html").exists()
    assert (output_dir / "books" / "sample-letters" / "letter-ii.html").exists()
