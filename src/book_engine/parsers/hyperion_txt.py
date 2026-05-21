from __future__ import annotations

import re
from pathlib import Path

from ..models import Section
from .gutenberg_txt import _paragraphize, extract_source_main_text


def parse_hyperion_epistolary(
    source_path: Path, title: str, source_format: str = "plain-txt"
) -> list[Section]:
    text = source_path.read_text(encoding="utf-8", errors="replace")
    main_text = extract_source_main_text(text, title, source_format=source_format)
    lines = [line.rstrip() for line in main_text.split("\n")]

    headings: list[tuple[int, str, str]] = []
    for index, line in enumerate(lines):
        match = re.fullmatch(r"(.+?)\s*\[([IVXLCDM]+)\]", line.strip())
        if match and " to " in match.group(1).lower():
            headings.append((index, match.group(1).strip(), match.group(2)))

    if not headings:
        raise RuntimeError("Could not locate first Hyperion epistolary section")

    sections: list[Section] = []
    for order, (start_index, correspondent, numeral) in enumerate(headings, start=1):
        end_index = headings[order][0] if order < len(headings) else len(lines)
        chunk_lines = lines[start_index + 1 : end_index]
        raw_body = "\n".join(chunk_lines).strip()
        paras = _paragraphize(raw_body)
        subtitle = paras[0] if paras and len(paras[0]) < 80 else ""
        body = paras[1:] if subtitle else paras
        sections.append(
            Section(
                id=f"letter-{numeral.lower()}",
                order=order,
                label=f"Letter {numeral}",
                title=correspondent,
                subtitle=subtitle,
                body=body,
            )
        )

    return sections
