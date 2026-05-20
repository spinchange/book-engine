from __future__ import annotations

import re
from pathlib import Path

from ..models import Section
from .gutenberg_txt import extract_gutenberg_main_text


def _paragraphize(raw_body: str) -> list[str]:
    paras: list[str] = []
    for part in re.split(r"\n\s*\n", raw_body):
        paragraph = re.sub(r"\s+", " ", part.strip())
        if paragraph:
            paras.append(paragraph)
    return paras


def parse_chaptered_text(source_path: Path, title: str) -> list[Section]:
    text = source_path.read_text(encoding="utf-8", errors="replace")
    main_text = extract_gutenberg_main_text(text, title)
    lines = [line.rstrip() for line in main_text.split("\n")]

    chapter_heading = re.compile(r"CHAPTER\s+([IVXLCDM]+|\d+)$")
    headings: list[tuple[int, str]] = []
    for index, line in enumerate(lines):
        if chapter_heading.fullmatch(line.strip()):
            headings.append((index, line.strip()))

    if not headings:
        raise RuntimeError("Could not locate any chapter headings")

    sections: list[Section] = []
    for order, (start_index, label) in enumerate(headings, start=1):
        end_index = headings[order][0] if order < len(headings) else len(lines)
        chunk_lines = lines[start_index + 1 : end_index]
        while chunk_lines and not chunk_lines[0].strip():
            chunk_lines.pop(0)

        title_line = ""
        if chunk_lines and chunk_lines[0].strip():
            title_line = chunk_lines.pop(0).strip()

        raw_body = "\n".join(chunk_lines).strip()
        body = _paragraphize(raw_body)
        chapter_id = label.lower().replace(" ", "-")
        readable_label = f"Chapter {label.split(maxsplit=1)[1]}"
        sections.append(
            Section(
                id=chapter_id,
                order=order,
                label=readable_label,
                title=title_line or readable_label,
                subtitle="",
                body=body,
            )
        )

    return sections
