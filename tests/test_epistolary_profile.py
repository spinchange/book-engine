from pathlib import Path

from book_engine.builder import build_library
from book_engine.parsers.gutenberg_txt import extract_gutenberg_main_text, parse_gutenberg_epistolary
from book_engine.parsers.hyperion_txt import parse_hyperion_epistolary


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


PLAIN_SAMPLE_LETTERS_TEXT = """I
_From A. to B._

Bath, Monday.

My dear friend,

I write to you at once.

II
_From B. to A._

London, Tuesday.

Your letter reached me.
"""


HYPERION_STYLE_TEXT = """Hyperion to Bellarmin [I]

Athens.

I have at last reached the islands of my longing.

Hyperion to Bellarmin [II]

Smyrna.

My heart is still full of Diotima.
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


SELF_MADE_MERCHANT_STYLE_TEXT = """*** START OF THE PROJECT GUTENBERG EBOOK LETTERS FROM A SELF-MADE MERCHANT TO HIS SON ***

LETTERS _from a_ SELF-MADE MERCHANT _to his_ SON

I

CHICAGO, October 1, 189-

_Dear Pierrepont:_ Your Ma got back safe this morning.

II

CHICAGO, May 4, 189-

_Dear Pierrepont:_ The cashier has just handed me your expense account.

*** END OF THE PROJECT GUTENBERG EBOOK LETTERS FROM A SELF-MADE MERCHANT TO HIS SON ***
"""


EVELINA_STYLE_TEXT = """*** START OF THE PROJECT GUTENBERG EBOOK EVELINA SAMPLE ***

THE HISTORY OF EVELINA

LETTER I

LADY HOWARD TO THE REV. MR. VILLARS Howard Grove, Kent.

Can any thing, my good Sir, be more painful to a friendly mind?

LETTER II

EVELINA IN CONTINUATION Queen Ann Street, April 5, Tuesday Morning.

I have a vast deal to say, and shall give all this morning to my pen.

LETTER III [Written some months after the last]

EVELINA TO THE REV. MR. VILLARS Queen Ann Street, London, Saturday,
April 2.

This moment arrived.

LETTER IV. [Inclosed in the preceding Letter.]

MR. VILLARS TO LADY HOWARD March 18. Dear Madam,

This letter will be delivered to you by my child.

*** END OF THE PROJECT GUTENBERG EBOOK EVELINA SAMPLE ***
"""


EVELINA_CONTINUATION_EDGE_CASES_TEXT = """*** START OF THE PROJECT GUTENBERG EBOOK EVELINA EDGE SAMPLE ***

THE HISTORY OF EVELINA

LETTER I

EVELINA IN CONTINUATION I HAVE a volume to write of the adventures of yesterday.

Miss Mirvan looked so much astonished that I was ready to laugh myself.

LETTER II

EVELINA IN CONTINUATION

June 10th
THIS morning Mr. Smith called,
on purpose, he said, to offer me a ticket.

Obvious as they must surely have been to any other person.

*** END OF THE PROJECT GUTENBERG EBOOK EVELINA EDGE SAMPLE ***
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


ELOISA_INLINE_HEADING_TEXT = """*** START OF THE PROJECT GUTENBERG EBOOK ELOISA SAMPLE ***

Eloisa

Volume I

Letter I. To Eloisa.

I must fly from you.

Letter II. From Eloisa.

You are too hasty.

Letter III. [6] To Eloisa.

I have received your last.

Letter IV. Answer to the Preceding.

I answer without delay.

*** END OF THE PROJECT GUTENBERG EBOOK ELOISA SAMPLE ***
"""


DUPLICATE_LABELS_TEXT = """*** START OF THE PROJECT GUTENBERG EBOOK DUPLICATE LABELS SAMPLE ***

Letter I. To Eloisa.

First body.

Letter I. From Eloisa.

Second body.

*** END OF THE PROJECT GUTENBERG EBOOK DUPLICATE LABELS SAMPLE ***
"""


LOWERCASE_FALSE_POSITIVE_TEXT = """*** START OF THE PROJECT GUTENBERG EBOOK LOWERCASE FALSE POSITIVE SAMPLE ***

Letter I. To Eloisa.

First body.

letter i have just hinted at.

Still the same letter body.

Letter II. From Eloisa.

Second body.

*** END OF THE PROJECT GUTENBERG EBOOK LOWERCASE FALSE POSITIVE SAMPLE ***
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


def test_parse_gutenberg_epistolary_supports_plain_text_sources(tmp_path: Path) -> None:
    source = tmp_path / "sample-letters-plain.txt"
    source.write_text(PLAIN_SAMPLE_LETTERS_TEXT, encoding="utf-8")

    sections = parse_gutenberg_epistolary(source, "Sample Letters", source_format="plain-txt")

    assert [section.id for section in sections] == ["letter-i", "letter-ii"]
    assert sections[0].title == "From A. to B."
    assert sections[0].subtitle == "Bath, Monday."
    assert sections[0].body == ["My dear friend,", "I write to you at once."]
    assert sections[1].title == "From B. to A."
    assert sections[1].subtitle == "London, Tuesday."
    assert sections[1].body == ["Your letter reached me."]


def test_parse_hyperion_epistolary_supports_bracketed_letter_headings(tmp_path: Path) -> None:
    source = tmp_path / "hyperion-sample.txt"
    source.write_text(HYPERION_STYLE_TEXT, encoding="utf-8")

    sections = parse_hyperion_epistolary(source, "Hyperion", source_format="plain-txt")

    assert [section.id for section in sections] == ["letter-i", "letter-ii"]
    assert [section.label for section in sections] == ["Letter I", "Letter II"]
    assert sections[0].title == "Hyperion to Bellarmin"
    assert sections[0].subtitle == "Athens."
    assert sections[0].body == ["I have at last reached the islands of my longing."]
    assert sections[1].title == "Hyperion to Bellarmin"
    assert sections[1].subtitle == "Smyrna."
    assert sections[1].body == ["My heart is still full of Diotima."]


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


def test_parse_gutenberg_epistolary_supports_self_made_merchant_style_roman_letters(tmp_path: Path) -> None:
    source = tmp_path / "self-made-merchant-sample.txt"
    source.write_text(SELF_MADE_MERCHANT_STYLE_TEXT, encoding="utf-8")

    sections = parse_gutenberg_epistolary(source, "Letters from a Self-Made Merchant to His Son")

    assert [section.id for section in sections] == ["letter-i", "letter-ii"]
    assert [section.label for section in sections] == ["Letter I", "Letter II"]
    assert sections[0].title == "Dear Pierrepont:"
    assert sections[0].subtitle == "CHICAGO, October 1, 189-"
    assert sections[0].body == ["Your Ma got back safe this morning."]
    assert sections[1].title == "Dear Pierrepont:"
    assert sections[1].subtitle == "CHICAGO, May 4, 189-"
    assert sections[1].body == ["The cashier has just handed me your expense account."]


def test_parse_gutenberg_epistolary_supports_evelina_style_mixed_case_headers(tmp_path: Path) -> None:
    source = tmp_path / "evelina-sample.txt"
    source.write_text(EVELINA_STYLE_TEXT, encoding="utf-8")

    sections = parse_gutenberg_epistolary(source, "Evelina Sample")

    assert [section.id for section in sections] == ["letter-i", "letter-ii", "letter-iii", "letter-iv"]
    assert sections[0].title == "LADY HOWARD TO THE REV. MR. VILLARS Howard Grove, Kent."
    assert sections[0].body == ["Can any thing, my good Sir, be more painful to a friendly mind?"]
    assert sections[1].title == "EVELINA IN CONTINUATION Queen Ann Street, April 5, Tuesday Morning."
    assert sections[1].body == ["I have a vast deal to say, and shall give all this morning to my pen."]
    assert sections[2].title == "EVELINA TO THE REV. MR. VILLARS Queen Ann Street, London, Saturday, April 2. [Written some months after the last]"
    assert sections[2].body == ["This moment arrived."]
    assert sections[3].title == "MR. VILLARS TO LADY HOWARD March 18. Dear Madam, [Inclosed in the preceding Letter.]"
    assert sections[3].body == ["This letter will be delivered to you by my child."]


def test_parse_gutenberg_epistolary_handles_evelina_continuation_body_edge_cases(tmp_path: Path) -> None:
    source = tmp_path / "evelina-edge-sample.txt"
    source.write_text(EVELINA_CONTINUATION_EDGE_CASES_TEXT, encoding="utf-8")

    sections = parse_gutenberg_epistolary(source, "Evelina Edge Sample")

    assert [section.id for section in sections] == ["letter-i", "letter-ii"]
    assert sections[0].title == "EVELINA IN CONTINUATION"
    assert sections[0].subtitle == ""
    assert sections[0].body == [
        "I HAVE a volume to write of the adventures of yesterday.",
        "Miss Mirvan looked so much astonished that I was ready to laugh myself.",
    ]
    assert sections[1].title == "EVELINA IN CONTINUATION"
    assert sections[1].subtitle == "June 10th"
    assert sections[1].body == [
        "THIS morning Mr. Smith called, on purpose, he said, to offer me a ticket.",
        "Obvious as they must surely have been to any other person.",
    ]


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


def test_parse_gutenberg_epistolary_supports_eloisa_inline_letter_headings(tmp_path: Path) -> None:
    source = tmp_path / "eloisa-inline-headings.txt"
    source.write_text(ELOISA_INLINE_HEADING_TEXT, encoding="utf-8")

    sections = parse_gutenberg_epistolary(source, "Eloisa Sample")

    assert [section.id for section in sections] == ["letter-i", "letter-ii", "letter-iii", "letter-iv"]
    assert [section.title for section in sections] == [
        "To Eloisa.",
        "From Eloisa.",
        "To Eloisa. [6]",
        "Answer to the Preceding.",
    ]
    assert sections[0].body == ["I must fly from you."]
    assert sections[1].body == ["You are too hasty."]
    assert sections[2].body == ["I have received your last."]
    assert sections[3].body == ["I answer without delay."]


def test_parse_gutenberg_epistolary_disambiguates_duplicate_letter_ids(tmp_path: Path) -> None:
    source = tmp_path / "duplicate-labels.txt"
    source.write_text(DUPLICATE_LABELS_TEXT, encoding="utf-8")

    sections = parse_gutenberg_epistolary(source, "Duplicate Labels Sample")

    assert [section.id for section in sections] == ["letter-i", "letter-i-2"]
    assert [section.label for section in sections] == ["Letter I", "Letter I"]
    assert [section.title for section in sections] == ["To Eloisa.", "From Eloisa."]


def test_parse_gutenberg_epistolary_rejects_lowercase_inline_false_positives(tmp_path: Path) -> None:
    source = tmp_path / "lowercase-false-positive.txt"
    source.write_text(LOWERCASE_FALSE_POSITIVE_TEXT, encoding="utf-8")

    sections = parse_gutenberg_epistolary(source, "Lowercase False Positive Sample")

    assert [section.id for section in sections] == ["letter-i", "letter-ii"]
    assert sections[0].body == ["First body.", "letter i have just hinted at.", "Still the same letter body."]
    assert sections[1].body == ["Second body."]


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


def test_build_library_supports_self_made_merchant_style_epistolary_book(tmp_path: Path) -> None:
    content_root = tmp_path / "library"
    books_dir = content_root / "books"
    merchant_dir = books_dir / "self-made-merchant-sample"
    merchant_dir.mkdir(parents=True)

    (content_root / "library.yaml").write_text(
        """title: Self-Made Merchant Library
books_dir: books
output_dir: dist
""",
        encoding="utf-8",
    )
    (merchant_dir / "book.yaml").write_text(
        """id: self-made-merchant-sample
title: Letters from a Self-Made Merchant to His Son
author: George Horace Lorimer
year: \"1902\"
source_file: source.txt
source_format: gutenberg-txt
profile: epistolary
parser: gutenberg-letters-v1
theme: classic-paper
""",
        encoding="utf-8",
    )
    (merchant_dir / "source.txt").write_text(SELF_MADE_MERCHANT_STYLE_TEXT, encoding="utf-8")

    output_dir = build_library(content_root)

    assert (output_dir / "index.html").exists()
    assert (output_dir / "books" / "self-made-merchant-sample" / "index.html").exists()
    assert (output_dir / "books" / "self-made-merchant-sample" / "letter-i.html").exists()
    assert (output_dir / "books" / "self-made-merchant-sample" / "letter-ii.html").exists()


def test_build_library_supports_evelina_style_epistolary_book(tmp_path: Path) -> None:
    content_root = tmp_path / "library"
    books_dir = content_root / "books"
    evelina_dir = books_dir / "evelina-sample"
    evelina_dir.mkdir(parents=True)

    (content_root / "library.yaml").write_text(
        """title: Evelina Library
books_dir: books
output_dir: dist
""",
        encoding="utf-8",
    )
    (evelina_dir / "book.yaml").write_text(
        """id: evelina-sample
title: Evelina Sample
author: Fanny Burney
year: \"1778\"
source_file: source.txt
source_format: gutenberg-txt
profile: epistolary
parser: gutenberg-letters-v1
theme: classic-paper
""",
        encoding="utf-8",
    )
    (evelina_dir / "source.txt").write_text(EVELINA_STYLE_TEXT, encoding="utf-8")

    output_dir = build_library(content_root)

    assert (output_dir / "index.html").exists()
    assert (output_dir / "books" / "evelina-sample" / "index.html").exists()
    assert (output_dir / "books" / "evelina-sample" / "letter-i.html").exists()
    assert (output_dir / "books" / "evelina-sample" / "letter-ii.html").exists()
    assert (output_dir / "books" / "evelina-sample" / "letter-iii.html").exists()
    assert (output_dir / "books" / "evelina-sample" / "letter-iv.html").exists()


def test_build_library_supports_plain_text_epistolary_book(tmp_path: Path) -> None:
    content_root = tmp_path / "library"
    books_dir = content_root / "books"
    plain_dir = books_dir / "plain-letters"
    plain_dir.mkdir(parents=True)

    (content_root / "library.yaml").write_text(
        """title: Plain Text Library
books_dir: books
output_dir: dist
""",
        encoding="utf-8",
    )
    (plain_dir / "book.yaml").write_text(
        """id: plain-letters
title: Plain Letters
author: Test Author
year: \"1902\"
source_file: source.txt
source_format: plain-txt
profile: epistolary
parser: gutenberg-letters-v1
theme: classic-paper
""",
        encoding="utf-8",
    )
    (plain_dir / "source.txt").write_text(PLAIN_SAMPLE_LETTERS_TEXT, encoding="utf-8")

    output_dir = build_library(content_root)

    assert (output_dir / "index.html").exists()
    assert (output_dir / "books" / "plain-letters" / "index.html").exists()
    assert (output_dir / "books" / "plain-letters" / "letter-i.html").exists()
    assert (output_dir / "books" / "plain-letters" / "letter-ii.html").exists()


def test_build_library_supports_hyperion_parser_on_plain_text_book(tmp_path: Path) -> None:
    content_root = tmp_path / "library"
    books_dir = content_root / "books"
    hyperion_dir = books_dir / "hyperion"
    hyperion_dir.mkdir(parents=True)

    (content_root / "library.yaml").write_text(
        """title: Hyperion Library
books_dir: books
output_dir: dist
""",
        encoding="utf-8",
    )
    (hyperion_dir / "book.yaml").write_text(
        """id: hyperion
title: Hyperion
author: Friedrich Holderlin
year: \"1819\"
source_file: source.txt
source_format: plain-txt
profile: epistolary
parser: hyperion-letters-v1
theme: classic-paper
""",
        encoding="utf-8",
    )
    (hyperion_dir / "source.txt").write_text(HYPERION_STYLE_TEXT, encoding="utf-8")

    output_dir = build_library(content_root)

    assert (output_dir / "index.html").exists()
    assert (output_dir / "books" / "hyperion" / "index.html").exists()
    assert (output_dir / "books" / "hyperion" / "letter-i.html").exists()
    assert (output_dir / "books" / "hyperion" / "letter-ii.html").exists()
