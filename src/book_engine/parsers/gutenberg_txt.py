from __future__ import annotations

import re
from pathlib import Path

from ..models import Section


def _normalize_source_text(text: str) -> str:
    return text.replace("\ufeff", "").replace("\r\n", "\n").strip()


def extract_gutenberg_main_text(text: str, title: str) -> str:
    text = _normalize_source_text(text)
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


def extract_source_main_text(text: str, title: str, source_format: str = "gutenberg-txt") -> str:
    if source_format == "gutenberg-txt":
        return extract_gutenberg_main_text(text, title)
    if source_format == "plain-txt":
        return _normalize_source_text(text)
    raise ValueError(f"Unsupported source format: {source_format}")


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
    if len(heading) < 4 or not heading[3].isupper():
        return False
    tail = [ln.strip() for ln in lines[index + 1 : index + 6] if ln.strip()]
    return bool(tail)


def _is_uppercaseish(line: str) -> bool:
    letters = [ch for ch in line if ch.isalpha()]
    if not letters:
        return False
    uppercase_letters = sum(1 for ch in letters if ch.isupper())
    return uppercase_letters / len(letters) >= 0.7



def _looks_like_date_line(line: str) -> bool:
    header = line.strip().upper()
    if not header:
        return False
    month_tokens = {
        "JAN",
        "FEB",
        "MAR",
        "APR",
        "MAY",
        "JUN",
        "JUL",
        "AUG",
        "SEP",
        "SEPT",
        "OCT",
        "NOV",
        "DEC",
        "MONDAY",
        "TUESDAY",
        "WEDNESDAY",
        "THURSDAY",
        "FRIDAY",
        "SATURDAY",
        "SUNDAY",
    }
    return any(token in header for token in month_tokens) and any(ch.isdigit() for ch in header)



def _looks_like_salutation_line(line: str) -> bool:
    header = line.strip()
    upper = header.upper()
    if not header.endswith((",", "!")):
        return False
    salutation_prefixes = (
        "DEAR ",
        "MY DEAR ",
        "MY DEAREST ",
        "O MY DEAR ",
        "O MY DEAREST ",
    )
    return _is_uppercaseish(header) and upper.startswith(salutation_prefixes)



def _normalize_global_correspondent_title(text: str) -> str:
    if not text.isupper():
        return text
    normalized = text.title()
    for token in (" A ", " An ", " And ", " Of ", " The ", " To "):
        normalized = normalized.replace(token, token.lower())
    return normalized



def _extract_global_correspondent_title(lines: list[str], index: int) -> str | None:
    previous_nonblank = [line.strip() for line in lines[max(0, index - 20) : index] if line.strip()]
    if not previous_nonblank:
        return None

    last = previous_nonblank[-1]
    if len(previous_nonblank) >= 2 and previous_nonblank[-2].upper() == "FROM" and " TO " in last.upper():
        return _normalize_global_correspondent_title(f"FROM {last}")

    if last.upper().startswith("FROM ") and " TO " in last.upper():
        return _normalize_global_correspondent_title(last)

    return None



def _looks_like_correspondent_header(lines: list[str]) -> bool:
    if not lines:
        return False

    first = lines[0].strip()
    first_upper = first.upper()
    if (
        (first_upper.startswith("TO ") and len(first) > 3 and first[3].isupper())
        or first_upper.startswith("FROM ")
        or ((_is_uppercaseish(first) and " TO " in first_upper))
        or ((_is_uppercaseish(first) and " FROM " in first_upper))
        or "[IN " in first_upper
        or "[ENCLOSED " in first_upper
    ):
        return True

    second = lines[1].strip() if len(lines) > 1 else ""
    second_upper = second.upper()
    if _is_uppercaseish(first) and (
        second_upper.startswith("[IN ") or second_upper.startswith("[ENCLOSED ")
    ):
        return True

    if _is_uppercaseish(first) and _looks_like_date_line(second):
        return True

    if _looks_like_salutation_line(first):
        return True

    if first_upper.startswith("[IN ") and _looks_like_salutation_line(second):
        return True

    if first_upper.startswith("[ENCLOSED ") and _looks_like_salutation_line(second):
        return True

    third = lines[2].strip() if len(lines) > 2 else ""
    if _is_uppercaseish(first) and (
        second_upper.startswith("[IN ") or second_upper.startswith("[ENCLOSED ")
    ) and _looks_like_date_line(third):
        return True

    return False



def _looks_like_letter_heading(lines: list[str], index: int) -> bool:
    heading = lines[index].strip()
    if not re.fullmatch(r"LETTER\s+[IVXLCDM]+\.?", heading):
        return False

    tail = [ln.strip() for ln in lines[index + 1 : index + 6] if ln.strip()]
    return _looks_like_correspondent_header(tail) or _extract_global_correspondent_title(lines, index) is not None


def _find_letter_heading_start(lines: list[str]) -> int | None:
    candidates = [i for i in range(len(lines)) if _looks_like_letter_heading(lines, i)]
    if not candidates:
        return None

    history_markers = [
        i for i, line in enumerate(lines) if line.strip().upper().startswith("THE HISTORY OF ")
    ]
    if history_markers:
        marker = history_markers[-1]
        for candidate in candidates:
            if candidate > marker:
                return candidate

    return candidates[0]



def _split_letter_heading_paragraphs(
    paras: list[str], fallback_label: str, global_title: str | None = None
) -> tuple[str, str, list[str]]:
    if not paras:
        return global_title or f"Letter {fallback_label}", "", []

    if global_title and not _looks_like_correspondent_header(paras[:3]):
        return global_title, "", paras

    title_text = paras[0]
    body_start = 1
    subtitle = ""

    if len(paras) > 1 and (
        paras[1].upper().startswith("[IN ") or paras[1].upper().startswith("[ENCLOSED ")
    ):
        title_text = f"{title_text} {paras[1]}"
        body_start = 2

    if len(paras) > body_start and _looks_like_date_line(paras[body_start]):
        subtitle = paras[body_start]
        body_start += 1
    elif title_text.upper().startswith("[IN ") or title_text.upper().startswith("[ENCLOSED "):
        if len(paras) > body_start and _looks_like_salutation_line(paras[body_start]):
            subtitle = paras[body_start]
            body_start += 1

    return title_text, subtitle, paras[body_start:]



def parse_gutenberg_epistolary(
    source_path: Path, title: str, source_format: str = "gutenberg-txt"
) -> list[Section]:
    text = source_path.read_text(encoding="utf-8", errors="replace")
    main_text = extract_source_main_text(text, title, source_format=source_format)
    lines = main_text.split("\n")

    heading_mode = None
    start_idx = None
    letter_heading_start = _find_letter_heading_start(lines)
    for i in range(len(lines) - 1):
        if _looks_like_roman_epistolary_heading(lines, i):
            start_idx = i
            heading_mode = "roman"
            break
        if letter_heading_start == i:
            start_idx = letter_heading_start
            heading_mode = "letter-heading"
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
    elif heading_mode == "letter-heading":
        for i in range(start_idx, len(lines)):
            if _looks_like_letter_heading(lines, i):
                match = re.fullmatch(r"LETTER\s+([IVXLCDM]+)\.?", lines[i].strip())
                if match:
                    headings.append((i, match.group(1)))
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
        elif heading_mode == "letter-heading":
            title_text, subtitle, body = _split_letter_heading_paragraphs(
                paras, label, _extract_global_correspondent_title(lines, line_no)
            )
            sec_id = f"letter-{label.lower()}"
            sec_label = f"Letter {label}"
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
