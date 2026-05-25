from __future__ import annotations

from html import escape
from pathlib import Path
import re

from .models import Book, Section


def build_front_matter_sections(book: Book) -> list[Section]:
    sections: list[Section] = []
    for index, entry in enumerate(book.config.front_matter, start=1):
        source_path = book.root / entry.source_file
        body = _load_front_matter_body(source_path, entry.title, entry.source_format)
        sections.append(
            Section(
                id=entry.id,
                order=index,
                label=entry.title,
                title=entry.title,
                subtitle="",
                body=body,
                kind="front-matter",
                body_format="html",
            )
        )
    return sections


def _load_front_matter_body(path: Path, title: str, source_format: str) -> list[str]:
    text = path.read_text(encoding="utf-8")
    source_format = source_format.lower()
    if source_format in {"markdown", "md"}:
        return _render_markdown_blocks(text, title)
    if source_format in {"plain", "plain-txt", "text", "txt"}:
        return _render_plain_blocks(text)
    raise ValueError(f"Unsupported front matter source format: {source_format}")


def _render_plain_blocks(text: str) -> list[str]:
    blocks = _split_blocks(text)
    return [f"<p>{_render_inline_markdown(block)}</p>" for block in blocks if block]


def _render_markdown_blocks(text: str, title: str) -> list[str]:
    blocks = _split_blocks(_strip_matching_h1(text, title))
    rendered: list[str] = []
    for block in blocks:
        lines = [line.strip() for line in block.splitlines() if line.strip()]
        if not lines:
            continue
        if all(line.startswith("- ") for line in lines):
            items = "".join(f"<li>{_render_inline_markdown(line[2:].strip())}</li>" for line in lines)
            rendered.append(f"<ul>{items}</ul>")
            continue
        if len(lines) == 1 and lines[0].startswith("## "):
            rendered.append(f"<h3>{_render_inline_markdown(lines[0][3:].strip())}</h3>")
            continue
        paragraph = " ".join(lines)
        rendered.append(f"<p>{_render_inline_markdown(paragraph)}</p>")
    return rendered


def _split_blocks(text: str) -> list[str]:
    normalized = text.replace("\r\n", "\n").strip()
    if not normalized:
        return []
    return [block.strip() for block in re.split(r"\n\s*\n", normalized) if block.strip()]


def _strip_matching_h1(text: str, title: str) -> str:
    normalized = text.replace("\r\n", "\n").lstrip("\ufeff")
    lines = normalized.splitlines()
    for index, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            continue
        heading = stripped[2:].strip() if stripped.startswith("# ") else None
        if heading and heading.casefold() == title.casefold():
            return "\n".join(lines[index + 1 :]).lstrip()
        return normalized
    return normalized


def _render_inline_markdown(text: str) -> str:
    rendered = escape(text)
    rendered = re.sub(r"\*(.+?)\*", r"<em>\1</em>", rendered)
    rendered = re.sub(r"_(.+?)_", r"<em>\1</em>", rendered)
    rendered = re.sub(r"`(.+?)`", r"<code>\1</code>", rendered)
    return rendered
