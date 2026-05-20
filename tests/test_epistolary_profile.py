from pathlib import Path

from book_engine.builder import build_library
from book_engine.parsers.gutenberg_txt import extract_gutenberg_main_text, parse_gutenberg_epistolary


HUMPHRY_CLINKER_TEXT = """*** START OF THE PROJECT GUTENBERG EBOOK 2160 ***

THE EXPEDITION OF HUMPHRY CLINKER

To Dr LEWIS.

DOCTOR,

The pills are good for nothing.

Send me another prescription.

To Miss LAETITIA WILLIS, at Gloucester.

MY DEAR MISS WILLIS,

We are all arrived safely.

The waters seem to agree with my uncle.

*** END OF THE PROJECT GUTENBERG EBOOK 2160 ***
"""


SAMPLE_LETTERS_TEXT = """*** START OF THE PROJECT GUTENBERG EBOOK SAMPLE LETTERS ***

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
"""


def test_extract_gutenberg_main_text_accepts_numeric_ebook_markers() -> None:
    main = extract_gutenberg_main_text(HUMPHRY_CLINKER_TEXT, "The Expedition of Humphry Clinker")

    assert main.startswith("THE EXPEDITION OF HUMPHRY CLINKER")
    assert "To Dr LEWIS." in main
    assert main.endswith("The waters seem to agree with my uncle.")


def test_parse_gutenberg_epistolary_supports_to_line_letters(tmp_path: Path) -> None:
    source = tmp_path / "humphry-clinker.txt"
    source.write_text(HUMPHRY_CLINKER_TEXT, encoding="utf-8")

    sections = parse_gutenberg_epistolary(source, "The Expedition of Humphry Clinker")

    assert [section.id for section in sections] == ["letter-1", "letter-2"]
    assert [section.label for section in sections] == ["Letter 1", "Letter 2"]
    assert sections[0].title == "To Dr LEWIS."
    assert sections[0].subtitle == "DOCTOR,"
    assert sections[0].body == [
        "The pills are good for nothing.",
        "Send me another prescription.",
    ]
    assert sections[1].title == "To Miss LAETITIA WILLIS, at Gloucester."
    assert sections[1].subtitle == "MY DEAR MISS WILLIS,"
    assert sections[1].body == [
        "We are all arrived safely.",
        "The waters seem to agree with my uncle.",
    ]


def test_build_library_supports_humphry_clinker_style_epistolary_book(tmp_path: Path) -> None:
    content_root = tmp_path / "library"
    books_dir = content_root / "books"
    book_dir = books_dir / "humphry-clinker"
    sample_dir = books_dir / "sample-letters"
    book_dir.mkdir(parents=True)
    sample_dir.mkdir(parents=True)

    (content_root / "library.yaml").write_text(
        """title: Mixed Library
books_dir: books
output_dir: dist
""",
        encoding="utf-8",
    )
    (book_dir / "book.yaml").write_text(
        """id: humphry-clinker
title: The Expedition of Humphry Clinker
author: Tobias Smollett
year: \"1771\"
source_file: source.txt
source_format: gutenberg-txt
profile: epistolary
parser: gutenberg-letters-v1
theme: classic-paper
""",
        encoding="utf-8",
    )
    (book_dir / "source.txt").write_text(HUMPHRY_CLINKER_TEXT, encoding="utf-8")

    (sample_dir / "book.yaml").write_text(
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
    (sample_dir / "source.txt").write_text(SAMPLE_LETTERS_TEXT, encoding="utf-8")

    output_dir = build_library(content_root)

    assert (output_dir / "index.html").exists()
    assert (output_dir / "books" / "humphry-clinker" / "letter-1.html").exists()
    assert (output_dir / "books" / "humphry-clinker" / "letter-2.html").exists()
    assert (output_dir / "books" / "sample-letters" / "letter-i.html").exists()
    assert (output_dir / "books" / "sample-letters" / "letter-ii.html").exists()
