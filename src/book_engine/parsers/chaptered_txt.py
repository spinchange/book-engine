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


def _parse_heading(line: str) -> tuple[str, str] | None:
    stripped = line.strip()
    prefix = "CHAPTER "
    if not stripped.startswith(prefix):
        return None

    remainder = stripped[len(prefix) :]
    match = re.match(r"([IVXLCDM]+|\d+)(.*)$", remainder)
    if not match:
        return None

    numeral = match.group(1)
    trailing = match.group(2).strip()
    inline_title = trailing.lstrip(".:-— ").strip()
    return f"CHAPTER {numeral}", inline_title


def _collect_wrapped_heading_title(lines: list[str], start_index: int, inline_title: str) -> str:
    title_parts: list[str] = []
    if inline_title:
        title_parts.append(inline_title)

    probe_index = start_index + 1
    while probe_index < len(lines):
        candidate = lines[probe_index].strip()
        if not candidate or candidate.startswith("CHAPTER "):
            break
        title_parts.append(candidate)
        probe_index += 1

    return re.sub(r"\s+", " ", " ".join(title_parts)).strip()


def parse_chaptered_text(source_path: Path, title: str) -> list[Section]:
    text = source_path.read_text(encoding="utf-8", errors="replace")
    main_text = extract_gutenberg_main_text(text, title)
    lines = [line.rstrip() for line in main_text.split("\n")]

    headings: list[tuple[int, str, str]] = []
    toc_titles: dict[str, str] = {}
    for index, line in enumerate(lines):
        parsed = _parse_heading(line)
        if not parsed:
            continue
        label, inline_title = parsed
        headings.append((index, label, inline_title))
        if inline_title and label not in toc_titles:
            toc_titles[label] = _collect_wrapped_heading_title(lines, index, inline_title)

    if not headings:
        raise RuntimeError("Could not locate any chapter headings")

    deduped_reversed: list[tuple[int, str, str]] = []
    seen_labels: set[str] = set()
    for heading in reversed(headings):
        _, label, _ = heading
        if label in seen_labels:
            continue
        seen_labels.add(label)
        deduped_reversed.append(heading)
    headings = list(reversed(deduped_reversed))

    sections: list[Section] = []
    for order, (start_index, label, inline_title) in enumerate(headings, start=1):
        end_index = headings[order][0] if order < len(headings) else len(lines)
        chunk_lines = lines[start_index + 1 : end_index]

        title_parts: list[str] = []
        if inline_title:
            title_parts.append(inline_title)
            while chunk_lines and not chunk_lines[0].strip():
                chunk_lines.pop(0)
            while chunk_lines and chunk_lines[0].strip():
                title_parts.append(chunk_lines.pop(0).strip())
            while chunk_lines and not chunk_lines[0].strip():
                chunk_lines.pop(0)
        else:
            while chunk_lines and not chunk_lines[0].strip():
                chunk_lines.pop(0)
            if label in toc_titles:
                title_parts.append(toc_titles[label])
            elif chunk_lines and chunk_lines[0].strip():
                while chunk_lines and chunk_lines[0].strip():
                    title_parts.append(chunk_lines.pop(0).strip())
                while chunk_lines and not chunk_lines[0].strip():
                    chunk_lines.pop(0)

        raw_body = "\n".join(chunk_lines).strip()
        body = _paragraphize(raw_body)
        chapter_id = label.lower().replace(" ", "-")
        readable_label = f"Chapter {label.split(maxsplit=1)[1]}"
        title_line = re.sub(r"\s+", " ", " ".join(title_parts)).strip()
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
