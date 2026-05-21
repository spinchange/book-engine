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

PLAIN_CHAPTERED_TEXT = """CHAPTER I
A Beginning

This is the first paragraph.

This is the second paragraph.

CHAPTER II
Another Turn

This is chapter two.
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

WERTHER_STYLE_TEXT = """*** START OF THE PROJECT GUTENBERG EBOOK 2527 ***

PREFACE

This is preface material.

BOOK I

MAY 4.

How happy I am that I am gone!

MAY 10.

A wonderful serenity has taken possession of my entire soul.

BOOK II.

OCTOBER 20.

We arrived here yesterday.

THE EDITOR TO THE READER.

It is a matter of extreme regret that we want original evidence.

*** END OF THE PROJECT GUTENBERG EBOOK 2527 ***
"""

PART_STYLE_TEXT = """*** START OF THE PROJECT GUTENBERG EBOOK NOTES FROM THE UNDERGROUND ***

PART I
Underground

I

I am a sick man.... I am a spiteful man.

II

I want now to tell you, gentlemen, whether you care to hear it or not.

PART II
A Propos of the Wet Snow

When from dark error's subjugation
My words of passionate exhortation
    Had wrenched thy fainting spirit free;

I

At that time I was only twenty-four.

*** END OF THE PROJECT GUTENBERG EBOOK NOTES FROM THE UNDERGROUND ***
"""

FRENCH_CHAPTERED_TEXT = """*** START OF THE PROJECT GUTENBERG EBOOK ADOLPHE ***

CHAPITRE PREMIER

Je venais de finir à vingt-deux ans mes études.

CHAPITRE II

Distrait, inattentif, ennuyé.

LETTRE À L'ÉDITEUR

Je vous renvoie, monsieur, le manuscrit.

RÉPONSE.

Oui, monsieur, je publierai le manuscrit.

*** END OF THE PROJECT GUTENBERG EBOOK ADOLPHE ***
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


def test_parse_chaptered_text_supports_plain_text_sources(tmp_path: Path) -> None:
    source = tmp_path / "sample-plain.txt"
    source.write_text(PLAIN_CHAPTERED_TEXT, encoding="utf-8")

    sections = parse_chaptered_text(source, "Sample Chaptered Book", source_format="plain-txt")

    assert [section.id for section in sections] == ["chapter-i", "chapter-ii"]
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


def test_parse_chaptered_text_supports_book_headings_and_editorial_coda(tmp_path: Path) -> None:
    source = tmp_path / "werther-style.txt"
    source.write_text(WERTHER_STYLE_TEXT, encoding="utf-8")

    sections = parse_chaptered_text(source, "The Sorrows of Young Werther")

    assert [section.id for section in sections] == ["book-i", "book-ii", "the-editor-to-the-reader"]
    assert [section.label for section in sections] == ["Book I", "Book II", "Editor"]
    assert sections[0].title == "Book I"
    assert sections[0].subtitle == "MAY 4."
    assert sections[0].body == [
        "How happy I am that I am gone!",
        "MAY 10.",
        "A wonderful serenity has taken possession of my entire soul.",
    ]
    assert sections[1].title == "Book II"
    assert sections[1].subtitle == "OCTOBER 20."
    assert sections[1].body == ["We arrived here yesterday."]
    assert sections[2].title == "The Editor to the Reader"
    assert sections[2].subtitle == ""
    assert sections[2].body == [
        "It is a matter of extreme regret that we want original evidence."
    ]


def test_parse_chaptered_text_supports_part_headings_with_titles(tmp_path: Path) -> None:
    source = tmp_path / "notes-from-underground.txt"
    source.write_text(PART_STYLE_TEXT, encoding="utf-8")

    sections = parse_chaptered_text(source, "Notes from the Underground")

    assert [section.id for section in sections] == ["part-i", "part-ii"]
    assert [section.label for section in sections] == ["Part I", "Part II"]
    assert sections[0].title == "Underground"
    assert sections[0].subtitle == ""
    assert sections[0].body == [
        "I",
        "I am a sick man.... I am a spiteful man.",
        "II",
        "I want now to tell you, gentlemen, whether you care to hear it or not.",
    ]
    assert sections[1].title == "A Propos of the Wet Snow"
    assert sections[1].subtitle == ""
    assert sections[1].body == [
        "When from dark error's subjugation My words of passionate exhortation Had wrenched thy fainting spirit free;",
        "I",
        "At that time I was only twenty-four.",
    ]


def test_parse_chaptered_text_supports_french_chapter_and_appendix_headings(tmp_path: Path) -> None:
    source = tmp_path / "adolphe-sample.txt"
    source.write_text(FRENCH_CHAPTERED_TEXT, encoding="utf-8")

    sections = parse_chaptered_text(source, "Adolphe")

    assert [section.id for section in sections] == [
        "chapitre-premier",
        "chapitre-ii",
        "lettre-a-l-editeur",
        "reponse",
    ]
    assert [section.label for section in sections] == [
        "Chapitre Premier",
        "Chapitre II",
        "Lettre à l'éditeur",
        "Réponse",
    ]
    assert sections[0].title == "Chapitre Premier"
    assert sections[0].body == ["Je venais de finir à vingt-deux ans mes études."]
    assert sections[1].body == ["Distrait, inattentif, ennuyé."]
    assert sections[2].title == "Lettre à l'éditeur"
    assert sections[2].body == ["Je vous renvoie, monsieur, le manuscrit."]
    assert sections[3].title == "Réponse"
    assert sections[3].body == ["Oui, monsieur, je publierai le manuscrit."]


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


def test_build_library_supports_plain_text_chaptered_book(tmp_path: Path) -> None:
    content_root = tmp_path / "library"
    books_dir = content_root / "books"
    chaptered_dir = books_dir / "plain-chaptered"
    chaptered_dir.mkdir(parents=True)

    (content_root / "library.yaml").write_text(
        """title: Plain Text Library
books_dir: books
output_dir: dist
""",
        encoding="utf-8",
    )
    (chaptered_dir / "book.yaml").write_text(
        """id: plain-chaptered
title: Plain Chaptered Book
author: Test Author
year: \"1903\"
source_file: source.txt
source_format: plain-txt
profile: chaptered
parser: gutenberg-chapters-v1
theme: classic-paper
""",
        encoding="utf-8",
    )
    (chaptered_dir / "source.txt").write_text(PLAIN_CHAPTERED_TEXT, encoding="utf-8")

    output_dir = build_library(content_root)

    assert (output_dir / "index.html").exists()
    assert (output_dir / "books" / "plain-chaptered" / "index.html").exists()
    assert (output_dir / "books" / "plain-chaptered" / "chapter-i.html").exists()
    assert (output_dir / "books" / "plain-chaptered" / "chapter-ii.html").exists()


def test_build_library_supports_werther_style_book_sections(tmp_path: Path) -> None:
    content_root = tmp_path / "library"
    books_dir = content_root / "books"
    werther_dir = books_dir / "werther"
    werther_dir.mkdir(parents=True)

    (content_root / "library.yaml").write_text(
        """title: Mixed Library
books_dir: books
output_dir: dist
""",
        encoding="utf-8",
    )
    (werther_dir / "book.yaml").write_text(
        """id: werther
title: The Sorrows of Young Werther
author: J.W. von Goethe
year: \"1774\"
source_file: source.txt
source_format: gutenberg-txt
profile: chaptered
parser: gutenberg-chapters-v1
theme: classic-paper
""",
        encoding="utf-8",
    )
    (werther_dir / "source.txt").write_text(WERTHER_STYLE_TEXT, encoding="utf-8")

    output_dir = build_library(content_root)

    assert (output_dir / "index.html").exists()
    assert (output_dir / "books" / "werther" / "book-i.html").exists()
    assert (output_dir / "books" / "werther" / "book-ii.html").exists()
    assert (output_dir / "books" / "werther" / "the-editor-to-the-reader.html").exists()

    toc_html = (output_dir / "books" / "werther" / "index.html").read_text(encoding="utf-8")
    assert '<span class="toc-kicker">Book I</span><span class="toc-meta">MAY 4.</span>' in toc_html
    assert 'Book I</span><span class="toc-title">Book I</span>' not in toc_html
    assert 'Editor</span><span class="toc-title">The Editor to the Reader</span>' not in toc_html
    assert '<span class="toc-title">The Editor to the Reader</span>' in toc_html

    book_i_html = (output_dir / "books" / "werther" / "book-i.html").read_text(encoding="utf-8")
    assert '<h2 class="letter-title">Book I</h2>' in book_i_html
    assert '<div class="letter-label">Book I</div>' not in book_i_html


def test_build_library_index_orders_books_alphabetically_by_title(tmp_path: Path) -> None:
    content_root = tmp_path / "library"
    books_dir = content_root / "books"
    zeta_title_dir = books_dir / "a-book"
    alpha_title_dir = books_dir / "z-book"
    zeta_title_dir.mkdir(parents=True)
    alpha_title_dir.mkdir(parents=True)

    (content_root / "library.yaml").write_text(
        """title: Mixed Library
books_dir: books
output_dir: dist
""",
        encoding="utf-8",
    )
    (zeta_title_dir / "book.yaml").write_text(
        """id: a-book
title: Zeta Letters
author: Test Author
year: \"1902\"
source_file: source.txt
source_format: gutenberg-txt
profile: epistolary
parser: gutenberg-letters-v1
theme: classic-paper
""",
        encoding="utf-8",
    )
    (alpha_title_dir / "book.yaml").write_text(
        """id: z-book
title: Alpha Letters
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
    letter_source = """*** START OF THE PROJECT GUTENBERG EBOOK SAMPLE LETTERS ***

I
_From A. to B._

Bath, Monday.

My dear friend,

I write to you at once.

*** END OF THE PROJECT GUTENBERG EBOOK SAMPLE LETTERS ***
"""
    (zeta_title_dir / "source.txt").write_text(letter_source, encoding="utf-8")
    (alpha_title_dir / "source.txt").write_text(letter_source, encoding="utf-8")

    output_dir = build_library(content_root)

    index_html = (output_dir / "index.html").read_text(encoding="utf-8")
    assert index_html.index("Alpha Letters") < index_html.index("Zeta Letters")
