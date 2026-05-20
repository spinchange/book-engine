from __future__ import annotations

import re
from pathlib import Path

from ..models import Section


def extract_gutenberg_main_text(text: str, title: str) -> str:
    text = text.replace("\ufeff", "").replace("\r\n", "\n")
    start_marker = f"*** START OF THE PROJECT GUTENBERG EBOOK {title.upper()} ***"
    end_marker = f"*** END OF THE PROJECT GUTENBERG EBOOK {title.upper()} ***"
    if start_marker in text and end_marker in text:
        start = text.index(start_marker) + len(start_marker)
        end = text.index(end_marker)
        return text[start:end].strip()

    generic_start = re.search(r"\*\*\* START OF THE PROJECT GUTENBERG EBOOK .*? \*\*\*", text)
    generic_end = re.search(r"\*\*\* END OF THE PROJECT GUTENBERG EBOOK .*? \*\*\*", text)
    if not generic_start or not generic_end:
        raise ValueError("Could not locate Project Gutenberg start/end markers")
    return text[generic_start.end() : generic_end.start()].strip()


def _paragraphize(raw_body: str) -> list[str]:
    paras: list[str] = []
    for part in re.split(r"\n\s*\n", raw_body):
        p = re.sub(r"\s+", " ", part.strip())
        if p:
            paras.append(p)
    return paras


def _looks_like_roman_epistolary_heading(lines: list[str], index: int) -> bool:
    if not re.fullmatch(r"[IVXLCDM]+", lines[index].strip()):
        return False
    tail = [ln.strip() for ln in lines[index + 1 : index + 6] if ln.strip()]
    return bool(tail and tail[0].startswith("_"))


def _looks_like_to_line_heading(lines: list[str], index: int) -> bool:
    heading = lines[index].strip()
    if not re.fullmatch(r"To\s+.+\.", heading):
        return False
    tail = [ln.strip() for ln in lines[index + 1 : index + 6] if ln.strip()]
    return bool(tail)


def parse_gutenberg_epistolary(source_path: Path, title: str) -> list[Section]:
    text = source_path.read_text(encoding="utf-8", errors="replace")
    main_text = extract_gutenberg_main_text(text, title)
    lines = main_text.split("\n")

    heading_mode = None
    start_idx = None
    for i in range(len(lines) - 1):
        if _looks_like_roman_epistolary_heading(lines, i):
            start_idx = i
            heading_mode = "roman"
            break
        if _looks_like_to_line_heading(lines, i):
            start_idx = i
            heading_mode = "to-line"
            break
    if start_idx is None or heading_mode is None:
        raise RuntimeError("Could not locate first epistolary section")

    headings: list[tuple[int, str]] = []
    if heading_mode == "roman":
        for i in range(start_idx, len(lines)):
            s = lines[i].strip()
            if _looks_like_roman_epistolary_heading(lines, i):
                headings.append((i, s))
            elif s == "CONCLUSION":
                headings.append((i, s))
    else:
        for i in range(start_idx, len(lines)):
            if _looks_like_to_line_heading(lines, i):
                headings.append((i, str(len(headings) + 1)))

    sections: list[Section] = []
    for index, (line_no, label) in enumerate(headings):
        end = headings[index + 1][0] if index + 1 < len(headings) else len(lines)
        chunk_lines = [line.rstrip() for line in lines[line_no:end]]
        raw_body = "\n".join(chunk_lines[1:]).strip()
        paras = _paragraphize(raw_body)

        if heading_mode == "roman":
            if paras and paras[0].startswith("_") and paras[0].endswith("_"):
                title_text = paras[0].strip("_")
                body = paras[1:]
            else:
                title_text = "Conclusion"
                body = paras
            subtitle = body[0] if body and len(body[0]) < 80 else ""
            if subtitle:
                body = body[1:]
            sec_id = "conclusion" if label == "CONCLUSION" else f"letter-{label.lower()}"
            sec_label = label if label == "CONCLUSION" else f"Letter {label}"
        else:
            title_text = chunk_lines[0].strip()
            subtitle = paras[0] if paras and len(paras[0]) < 80 else ""
            body = paras[1:] if subtitle else paras
            sec_id = f"letter-{index + 1}"
            sec_label = f"Letter {index + 1}"

        sections.append(
            Section(
                id=sec_id,
                order=index + 1,
                label=sec_label,
                title=title_text,
                subtitle=subtitle,
                body=body,
            )
        )
    return sections
