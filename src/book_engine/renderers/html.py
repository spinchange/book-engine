from __future__ import annotations

from html import escape
from pathlib import Path

from ..models import Book, Section

CSS = """
:root {
  --paper: #fffdf7;
  --ink: #22201c;
  --muted: #6b6258;
  --accent: #7c4f2b;
  --accent-soft: #efe3d2;
  --border: #d8c7ad;
  --shadow: 0 20px 60px rgba(60, 40, 20, 0.12);
}
* { box-sizing: border-box; }
body { margin: 0; font-family: Georgia, 'Times New Roman', serif; background: linear-gradient(180deg, #f4ecd8 0%, #efe4cd 100%); color: var(--ink); line-height: 1.7; }
a { color: var(--accent); }
.header { padding: 3rem 1.5rem 1rem; text-align: center; }
.header h1 { margin: 0; font-size: clamp(2.2rem, 4vw, 3.6rem); }
.header p { color: var(--muted); margin: 0.6rem auto 0; max-width: 52rem; }
.container { width: min(920px, calc(100% - 2rem)); margin: 0 auto 3rem; background: var(--paper); border: 1px solid var(--border); border-radius: 18px; box-shadow: var(--shadow); padding: 2rem; }
.toc-list { list-style: none; padding: 0; margin: 1.5rem 0 0; }
.toc-list li { border-top: 1px solid var(--accent-soft); }
.toc-list li:first-child { border-top: none; }
.toc-list a { display: block; padding: 1rem 0; text-decoration: none; color: inherit; }
.toc-list a:hover .toc-title { text-decoration: underline; }
.toc-kicker { display: inline-block; min-width: 8rem; color: var(--accent); font-weight: 700; }
.toc-title { font-weight: 700; }
.toc-meta { display: block; color: var(--muted); font-size: 0.98rem; margin-top: 0.2rem; }
.page-nav { display: flex; justify-content: space-between; gap: 1rem; margin: 2rem 0 1rem; padding-top: 1rem; border-top: 1px solid var(--accent-soft); }
.page-nav a, .page-nav span { flex: 1; }
.page-nav .center { text-align: center; }
.page-nav .right { text-align: right; }
.book-grid { display: grid; gap: 1rem; }
.book-card { border: 1px solid var(--accent-soft); border-radius: 12px; padding: 1rem 1.2rem; background: #fffaf0; }
.book-card h3 { margin: 0 0 .3rem; }
.letter-label { color: var(--accent); text-transform: uppercase; letter-spacing: 0.16em; font-size: .85rem; margin-bottom: .5rem; }
.letter-title { margin: 0; font-size: clamp(2rem, 3vw, 3rem); }
.letter-subtitle, .source-note, .muted { color: var(--muted); }
.letter-body, .front-matter-body { margin-top: 2rem; font-size: 1.12rem; }
.letter-body p, .front-matter-body p { margin: 1rem 0; }
.letter-body p:first-of-type::first-letter { float: left; font-size: 3.4rem; line-height: .9; padding-right: .4rem; color: var(--accent); }
.front-matter-body h3 { margin-top: 2rem; }
.front-matter-body ul { margin: 1rem 0 1rem 1.5rem; }
.credit { margin-top: 2rem; padding-top: 1rem; border-top: 1px solid var(--accent-soft); color: var(--muted); font-size: .95rem; }
@media (max-width: 640px) { .container { padding: 1.25rem; } .page-nav { flex-direction: column; } .page-nav .center, .page-nav .right { text-align: left; } .toc-kicker { display: block; min-width: 0; margin-bottom: .2rem; } }
"""


def _page(title: str, body: str) -> str:
    return f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(title)}</title>
  <style>{CSS}</style>
</head>
<body>{body}</body>
</html>'''


def _nav(prev_section: Section | None, next_section: Section | None) -> str:
    left = f'<a href="{prev_section.id}.html">← {escape(prev_section.label)}</a>' if prev_section else '<span></span>'
    center = '<a class="center" href="index.html">Table of contents</a>'
    right = f'<a class="right" href="{next_section.id}.html">{escape(next_section.label)} →</a>' if next_section else '<span class="right"></span>'
    return f'<nav class="page-nav">{left}{center}{right}</nav>'


def render_library_index(library: dict, books: list[Book], output_dir: Path) -> None:
    cards = []
    for book in sorted(books, key=lambda book: (book.config.title.casefold(), book.config.author.casefold(), book.config.id)):
        description = book.config.description or "A generated reading edition."
        cards.append(
            f'<article class="book-card"><h3><a href="books/{book.output_slug}/index.html">{escape(book.config.title)}</a></h3>'
            f'<p class="muted">{escape(book.config.author)} · {escape(book.config.year)}</p>'
            f'<p>{escape(description)}</p></article>'
        )
    body = f'''
<header class="header">
  <h1>{escape(library.get("title", "Library"))}</h1>
  <p>{escape(library.get("description", "A library of books rendered as linked HTML reading editions."))}</p>
</header>
<main class="container">
  <h2>Books</h2>
  <section class="book-grid">{"".join(cards)}</section>
</main>'''
    (output_dir / 'index.html').write_text(_page(library.get('title', 'Library'), body), encoding='utf-8')


def render_book(book: Book, output_dir: Path) -> None:
    book_dir = output_dir / 'books' / book.output_slug
    book_dir.mkdir(parents=True, exist_ok=True)

    toc_items = []
    for sec in book.sections:
        meta_html = f'<span class="toc-meta">{escape(sec.subtitle)}</span>' if sec.subtitle else ''
        show_kicker = sec.kind != 'front-matter' and not (sec.label == 'Editor' and sec.title.lower().startswith('the editor'))
        kicker_html = f'<span class="toc-kicker">{escape(sec.label)}</span>' if show_kicker else ''
        title_html = f'<span class="toc-title">{escape(sec.title)}</span>' if sec.kind == 'front-matter' or sec.title != sec.label else ''
        toc_items.append(
            f'<li><a href="{sec.id}.html">{kicker_html}'
            f'{title_html}{meta_html}</a></li>'
        )

    source_html = f'Source: <a href="{escape(book.config.source_url)}">Project Gutenberg</a>' if book.config.source_url else ''
    index_body = f'''
<header class="header">
  <h1>{escape(book.config.title)}</h1>
  <p>By {escape(book.config.author)} · {escape(book.config.year)}</p>
</header>
<main class="container">
  <h2>Table of Contents</h2>
  <p class="source-note">{source_html}</p>
  <ol class="toc-list">{"".join(toc_items)}</ol>
  <p class="credit"><a href="../../index.html">Back to library</a></p>
</main>'''
    (book_dir / 'index.html').write_text(_page(f'{book.config.title} — Table of Contents', index_body), encoding='utf-8')

    for idx, sec in enumerate(book.sections):
        prev_sec = book.sections[idx - 1] if idx > 0 else None
        next_sec = book.sections[idx + 1] if idx + 1 < len(book.sections) else None
        body_content = ''.join(sec.body) if sec.body_format == 'html' else ''.join(f'<p>{escape(p)}</p>' for p in sec.body)
        subtitle_html = f'<p class="letter-subtitle">{escape(sec.subtitle)}</p>' if sec.subtitle else ''
        label_html = '' if sec.kind == 'front-matter' or sec.title == sec.label else f'<div class="letter-label">{escape(sec.label)}</div>'
        body_class = 'front-matter-body' if sec.kind == 'front-matter' else 'letter-body'
        page_body = f'''
<header class="header">
  <h1>{escape(book.config.title)}</h1>
  <p>By {escape(book.config.author)} · Sequential reading edition</p>
</header>
<main class="container">
  {label_html}
  <h2 class="letter-title">{escape(sec.title)}</h2>
  {subtitle_html}
  {_nav(prev_sec, next_sec)}
  <section class="{body_class}">{body_content}</section>
  {_nav(prev_sec, next_sec)}
  <p class="credit"><a href="index.html">Book contents</a> · <a href="../../index.html">Library index</a></p>
</main>'''
        page_title = sec.title if sec.kind == 'front-matter' else sec.label
        (book_dir / f'{sec.id}.html').write_text(_page(f'{book.config.title} — {page_title}', page_body), encoding='utf-8')
