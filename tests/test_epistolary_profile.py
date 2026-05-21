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


CLARISSA_STYLE_TEXT = """*** START OF THE PROJECT GUTENBERG EBOOK CLARISSA SAMPLE ***

SUMMARY OF THE LETTERS OF VOLUME I

LETTER I. Miss Howe to Miss Clarissa Harlowe.—Summary text.

THE HISTORY OF CLARISSA HARLOWE

LETTER I

MISS ANNA HOWE, TO MISS CLARISSA HARLOWE JAN 10.

I am extremely concerned, my dearest friend.

LETTER II

MISS CLARISSA HARLOWE, TO MISS ANNA HOWE JAN. 11.

I will obey your commands.

*** END OF THE PROJECT GUTENBERG EBOOK CLARISSA SAMPLE ***
"""


CLARISSA_SPLIT_SUMMARY_TEXT = """*** START OF THE PROJECT GUTENBERG EBOOK CLARISSA SAMPLE ***

SUMMARY OF THE LETTERS OF VOLUME I

LETTER I

MISS HOWE TO MISS CLARISSA HARLOWE.

Summary text.

THE HISTORY OF CLARISSA HARLOWE

LETTER I

MISS ANNA HOWE, TO MISS CLARISSA HARLOWE JAN 10.

I am extremely concerned, my dearest friend.

LETTER II

TO ROBERT LOVELACE, ESQ. TUESDAY NIGHT, APRIL 18.

DEAR SIR,

This is a line-start TO heading.

LETTER III

MISS CLARISSA HARLOWE [IN CONTINUATION.]

This is a continuation heading.

LETTER IV

MR. LOVELACE

[IN CONTINUATION.]

THURSDAY, JULY 20.

This is a multiline continuation heading.

*** END OF THE PROJECT GUTENBERG EBOOK CLARISSA SAMPLE ***
"""


PAMELA_STYLE_TEXT = """*** START OF THE PROJECT GUTENBERG EBOOK PAMELA SAMPLE ***

PAMELA, or VIRTUE REWARDED

LETTER I

DEAR FATHER AND MOTHER,

I have great trouble, and some comfort, to acquaint you with.

LETTER II

[In answer to the preceding.]

DEAR PAMELA,

Your letter was indeed a great trouble, and some comfort, to me.

LETTER III

MY DEAR FATHER AND MOTHER,

I write again to assure you of my duty.

LETTER IV

O MY DEAREST FATHER AND MOTHER!

Let me write, and bewail my miserable hard fate.

*** END OF THE PROJECT GUTENBERG EBOOK PAMELA SAMPLE ***
"""


PORTUGUESE_NUN_STYLE_TEXT = """*** START OF THE PROJECT GUTENBERG EBOOK THE LETTERS OF A PORTUGUESE NUN ***

CONTENTS

LETTER I

To think I am scorned, and left by faithless you.

FROM

A NUN TO A CAVALIER

LETTER I

Oh! the unhappy Joys which Love contains.

LETTER II

From a Nun to a Cavalier

Alas! it is impossible to tell.

*** END OF THE PROJECT GUTENBERG EBOOK THE LETTERS OF A PORTUGUESE NUN ***
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


def test_parse_gutenberg_epistolary_supports_clarissa_style_letter_headings(tmp_path: Path) -> None:
    source = tmp_path / "clarissa-sample.txt"
    source.write_text(CLARISSA_STYLE_TEXT, encoding="utf-8")

    sections = parse_gutenberg_epistolary(source, "Clarissa Sample")

    assert [section.id for section in sections] == ["letter-i", "letter-ii"]
    assert [section.label for section in sections] == ["Letter I", "Letter II"]
    assert sections[0].title == "MISS ANNA HOWE, TO MISS CLARISSA HARLOWE JAN 10."
    assert sections[0].subtitle == ""
    assert sections[0].body == ["I am extremely concerned, my dearest friend."]
    assert sections[1].title == "MISS CLARISSA HARLOWE, TO MISS ANNA HOWE JAN. 11."
    assert sections[1].body == ["I will obey your commands."]


def test_parse_gutenberg_epistolary_skips_split_summary_and_supports_additional_clarissa_headers(tmp_path: Path) -> None:
    source = tmp_path / "clarissa-split-summary.txt"
    source.write_text(CLARISSA_SPLIT_SUMMARY_TEXT, encoding="utf-8")

    sections = parse_gutenberg_epistolary(source, "Clarissa Sample")

    assert [section.id for section in sections] == ["letter-i", "letter-ii", "letter-iii", "letter-iv"]
    assert sections[0].title == "MISS ANNA HOWE, TO MISS CLARISSA HARLOWE JAN 10."
    assert sections[1].title == "TO ROBERT LOVELACE, ESQ. TUESDAY NIGHT, APRIL 18."
    assert sections[1].body == ["DEAR SIR,", "This is a line-start TO heading."]
    assert sections[2].title == "MISS CLARISSA HARLOWE [IN CONTINUATION.]"
    assert sections[2].body == ["This is a continuation heading."]
    assert sections[3].title == "MR. LOVELACE [IN CONTINUATION.]"
    assert sections[3].subtitle == "THURSDAY, JULY 20."
    assert sections[3].body == ["This is a multiline continuation heading."]


def test_parse_gutenberg_epistolary_supports_pamela_style_letter_headings(tmp_path: Path) -> None:
    source = tmp_path / "pamela-sample.txt"
    source.write_text(PAMELA_STYLE_TEXT, encoding="utf-8")

    sections = parse_gutenberg_epistolary(source, "Pamela Sample")

    assert [section.id for section in sections] == ["letter-i", "letter-ii", "letter-iii", "letter-iv"]
    assert sections[0].title == "DEAR FATHER AND MOTHER,"
    assert sections[0].subtitle == ""
    assert sections[0].body == ["I have great trouble, and some comfort, to acquaint you with."]
    assert sections[1].title == "[In answer to the preceding.]"
    assert sections[1].subtitle == "DEAR PAMELA,"
    assert sections[1].body == ["Your letter was indeed a great trouble, and some comfort, to me."]
    assert sections[2].title == "MY DEAR FATHER AND MOTHER,"
    assert sections[2].body == ["I write again to assure you of my duty."]
    assert sections[3].title == "O MY DEAREST FATHER AND MOTHER!"
    assert sections[3].body == ["Let me write, and bewail my miserable hard fate."]


def test_parse_gutenberg_epistolary_skips_contents_false_positives_and_supports_global_correspondent_titles(tmp_path: Path) -> None:
    source = tmp_path / "portuguese-nun-sample.txt"
    source.write_text(PORTUGUESE_NUN_STYLE_TEXT, encoding="utf-8")

    sections = parse_gutenberg_epistolary(source, "The Letters of a Portuguese Nun")

    assert [section.id for section in sections] == ["letter-i", "letter-ii"]
    assert sections[0].title == "From a Nun to a Cavalier"
    assert sections[0].subtitle == ""
    assert sections[0].body == ["Oh! the unhappy Joys which Love contains."]
    assert sections[1].title == "From a Nun to a Cavalier"
    assert sections[1].body == ["Alas! it is impossible to tell."]


def test_build_library_supports_humphry_clinker_style_epistolary_book(tmp_path: Path) -> None:
    content_root = tmp_path / "library"
    books_dir = content_root / "books"
    book_dir = books_dir / "humphry-clinker"
    sample_dir = books_dir / "sample-letters"
    clarissa_dir = books_dir / "clarissa-sample"
    book_dir.mkdir(parents=True)
    sample_dir.mkdir(parents=True)
    clarissa_dir.mkdir(parents=True)

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

    (clarissa_dir / "book.yaml").write_text(
        """id: clarissa-sample
title: Clarissa Sample
author: Samuel Richardson
year: \"1748\"
source_file: source.txt
source_format: gutenberg-txt
profile: epistolary
parser: gutenberg-letters-v1
theme: classic-paper
""",
        encoding="utf-8",
    )
    (clarissa_dir / "source.txt").write_text(CLARISSA_STYLE_TEXT, encoding="utf-8")

    output_dir = build_library(content_root)

    assert (output_dir / "index.html").exists()
    assert (output_dir / "books" / "humphry-clinker" / "letter-1.html").exists()
    assert (output_dir / "books" / "humphry-clinker" / "letter-2.html").exists()
    assert (output_dir / "books" / "sample-letters" / "letter-i.html").exists()
    assert (output_dir / "books" / "sample-letters" / "letter-ii.html").exists()
    assert (output_dir / "books" / "clarissa-sample" / "letter-i.html").exists()
    assert (output_dir / "books" / "clarissa-sample" / "letter-ii.html").exists()


def test_build_library_supports_pamela_style_epistolary_book(tmp_path: Path) -> None:
    content_root = tmp_path / "library"
    books_dir = content_root / "books"
    pamela_dir = books_dir / "pamela-sample"
    pamela_dir.mkdir(parents=True)

    (content_root / "library.yaml").write_text(
        """title: Pamela Library
books_dir: books
output_dir: dist
""",
        encoding="utf-8",
    )
    (pamela_dir / "book.yaml").write_text(
        """id: pamela-sample
title: Pamela Sample
author: Samuel Richardson
year: \"1740\"
source_file: source.txt
source_format: gutenberg-txt
profile: epistolary
parser: gutenberg-letters-v1
theme: classic-paper
""",
        encoding="utf-8",
    )
    (pamela_dir / "source.txt").write_text(PAMELA_STYLE_TEXT, encoding="utf-8")

    output_dir = build_library(content_root)

    assert (output_dir / "index.html").exists()
    assert (output_dir / "books" / "pamela-sample" / "index.html").exists()
    assert (output_dir / "books" / "pamela-sample" / "letter-i.html").exists()
    assert (output_dir / "books" / "pamela-sample" / "letter-ii.html").exists()
    assert (output_dir / "books" / "pamela-sample" / "letter-iii.html").exists()
    assert (output_dir / "books" / "pamela-sample" / "letter-iv.html").exists()
