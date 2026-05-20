from __future__ import annotations

import re
from pathlib import Path

from ..models import Section


def extract_gutenberg_main_text(text: str, title: str) -> str:
    text = text.replace("\ufeff", "").replace("\r\n", "\n")
    start_marker = f"*** START OF THE PROJECT GUTENBERG EBOOK {title.upper()} ***"
    end_marker = f"*** END OF THE PROJECT GUTENBERG EBOOK {title.upper()} ***"
    if start_marker not in text or end_marker not in text:
        raise ValueError("Could not locate Project Gutenberg start/end markers")
    start = text.index(start_marker) + len(start_marker)
    end = text.index(end_marker)
    return text[start:end].strip()


def _paragraphize(raw_body: str) -> list[str]:
    paras: list[str] = []
    for part in re.split(r"\n\s*\n", raw_body):
        p = re.sub(r"\s+", " ", part.strip())
        if p:
            paras.append(p)
    return paras


def parse_gutenberg_epistolary(source_path: Path, title: str) -> list[Section]:
    text = source_path.read_text(encoding="utf-8", errors="replace")
    main_text = extract_gutenberg_main_text(text, title)
    lines = main_text.split("\n")

    start_idx = None
    for i in range(len(lines) - 3):
        if re.fullmatch(r"[IVXLCDM]+", lines[i].strip()):
            tail = [ln.strip() for ln in lines[i + 1 : i + 6] if ln.strip()]
            if tail and tail[0].startswith("_"):
                start_idx = i
                break
    if start_idx is None:
        raise RuntimeError("Could not locate first epistolary section")

    headings: list[tuple[int, str]] = []
    for i in range(start_idx, len(lines)):
        s = lines[i].strip()
        if re.fullmatch(r"[IVXLCDM]+", s):
            tail = [ln.strip() for ln in lines[i + 1 : i + 6] if ln.strip()]
            if tail and tail[0].startswith("_"):
                headings.append((i, s))
        elif s == "CONCLUSION":
            headings.append((i, s))

    sections: list[Section] = []
    for index, (line_no, label) in enumerate(headings):
        end = headings[index + 1][0] if index + 1 < len(headings) else len(lines)
        chunk = "\n".join(lines[line_no:end]).strip()
        raw_body = "\n".join(chunk.split("\n")[1:]).strip()
        paras = _paragraphize(raw_body)
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
