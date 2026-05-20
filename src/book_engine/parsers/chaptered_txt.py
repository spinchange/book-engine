from __future__ import annotations

import re
from pathlib import Path

from ..models import Section
from .gutenberg_txt import extract_gutenberg_main_text


def _paragraphize(raw_body: str) -> list[str]:
    lines = raw_body.split("\n")
    blank_runs_between_content: list[int] = []
    seen_content = False
    blank_run = 0
    for line in lines:
        if line.strip():
            if seen_content and blank_run > 0:
                blank_runs_between_content.append(blank_run)
            seen_content = True
            blank_run = 0
        else:
            blank_run += 1

    sparse_wrapped_mode = (
        any(run >= 2 for run in blank_runs_between_content)
        and sum(1 for run in blank_runs_between_content if run == 1)
        > sum(1 for run in blank_runs_between_content if run >= 2)
    )

    if not sparse_wrapped_mode:
        return [
            re.sub(r"\s+", " ", part.strip())
            for part in re.split(r"\n\s*\n", raw_body)
            if part.strip()
        ]

    paras: list[str] = []
    current_lines: list[str] = []
    blank_run = 0
    for line in lines:
        stripped = line.strip()
        if stripped:
            if blank_run >= 2 and current_lines:
                paras.append(" ".join(current_lines))
                current_lines = []
            current_lines.append(stripped)
            blank_run = 0
        else:
            blank_run += 1
    if current_lines:
        paras.append(" ".join(current_lines))
    return [re.sub(r"\s+", " ", paragraph).strip() for paragraph in paras if paragraph.strip()]


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


def _consume_sparse_wrapped_title_block(chunk_lines: list[str]) -> tuple[list[str], list[str]] | None:
    probe_index = 0
    while probe_index < len(chunk_lines) and not chunk_lines[probe_index].strip():
        probe_index += 1

    if probe_index >= len(chunk_lines):
        return None

    title_parts: list[str] = []
    blank_run = 0
    scan_index = probe_index
    while scan_index < len(chunk_lines):
        candidate = chunk_lines[scan_index].strip()
        if candidate.startswith("CHAPTER "):
            break
        if candidate:
            title_parts.append(candidate)
            blank_run = 0
        else:
            blank_run += 1
            if blank_run >= 2:
                remainder = chunk_lines[scan_index:]
                return title_parts, remainder
        scan_index += 1

    return None


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
            else:
                sparse_wrapped_title = _consume_sparse_wrapped_title_block(chunk_lines)
                if sparse_wrapped_title is not None:
                    title_parts, chunk_lines = sparse_wrapped_title
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
