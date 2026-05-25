from pathlib import Path

from book_engine.builder import build_library
from book_engine.config import load_book_config


SAMPLE_CHAPTERED_TEXT = """*** START OF THE PROJECT GUTENBERG EBOOK SAMPLE BOOK ***

CHAPTER I
The Opening Chapter

This is the first paragraph of the opening chapter.

CHAPTER II
The Second Chapter

This is the second chapter.

*** END OF THE PROJECT GUTENBERG EBOOK SAMPLE BOOK ***
"""


TRANSLATOR_NOTE_MARKDOWN = """# Translator's Note

This translation of *Persian Letters* was made one letter at a time.

That method shaped the edition.
"""


def test_load_book_config_supports_front_matter_entries(tmp_path: Path) -> None:
    book_yaml = tmp_path / "book.yaml"
    book_yaml.write_text(
        """id: sample-book
title: Sample Book
author: Test Author
year: "1900"
source_file: source.txt
source_format: gutenberg-txt
profile: chaptered
parser: gutenberg-chapters-v1
theme: classic-paper
front_matter:
  - id: translators-note
    title: Translator's Note
    source_file: translator-note.md
""",
        encoding="utf-8",
    )

    config = load_book_config(book_yaml)

    assert len(config.front_matter) == 1
    assert config.front_matter[0].id == "translators-note"
    assert config.front_matter[0].title == "Translator's Note"
    assert config.front_matter[0].source_file == "translator-note.md"


def test_build_library_renders_front_matter_before_main_sections(tmp_path: Path) -> None:
    content_root = tmp_path / "library"
    books_dir = content_root / "books"
    book_dir = books_dir / "sample-book"
    book_dir.mkdir(parents=True)

    (content_root / "library.yaml").write_text(
        """title: Front Matter Library
books_dir: books
output_dir: dist
""",
        encoding="utf-8",
    )
    (book_dir / "book.yaml").write_text(
        """id: sample-book
title: Sample Book
author: Test Author
year: "1900"
source_file: source.txt
source_format: gutenberg-txt
profile: chaptered
parser: gutenberg-chapters-v1
theme: classic-paper
front_matter:
  - id: translators-note
    title: Translator's Note
    source_file: translator-note.md
""",
        encoding="utf-8",
    )
    (book_dir / "source.txt").write_text(SAMPLE_CHAPTERED_TEXT, encoding="utf-8")
    (book_dir / "translator-note.md").write_text(TRANSLATOR_NOTE_MARKDOWN, encoding="utf-8")

    output_dir = build_library(content_root)

    note_path = output_dir / "books" / "sample-book" / "translators-note.html"
    chapter_path = output_dir / "books" / "sample-book" / "chapter-i.html"
    assert note_path.exists()
    assert chapter_path.exists()

    toc_html = (output_dir / "books" / "sample-book" / "index.html").read_text(encoding="utf-8")
    assert toc_html.index("translators-note.html") < toc_html.index("chapter-i.html")
    assert '<span class="toc-title">Translator&#x27;s Note</span>' in toc_html

    note_html = note_path.read_text(encoding="utf-8")
    assert '<h2 class="letter-title">Translator&#x27;s Note</h2>' in note_html
    assert '<em>Persian Letters</em>' in note_html
    assert 'That method shaped the edition.' in note_html
    assert 'Chapter I →' in note_html

    chapter_html = chapter_path.read_text(encoding="utf-8")
    assert '← Translator&#x27;s Note' in chapter_html
