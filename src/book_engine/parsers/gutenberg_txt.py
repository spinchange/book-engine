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


def _looks_like_roman_epistolary_heading(lines: list[str], index: int) -> bool:
    if not re.fullmatch(r"[IVXLCDM]+", lines[index].strip()):
        return False
    tail = [ln.strip() for ln in lines[index + 1 : index + 6] if ln.strip()]
    if tail and tail[0].startswith("_"):
        return True
    if len(tail) >= 2 and _looks_like_date_line(tail[0]) and bool(_split_italic_salutation_paragraph(tail[1])):
        return True
    return _looks_like_correspondent_header(tail)


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


def _looks_like_brief_dateline_line(line: str) -> bool:
    header = re.sub(r"\s+", " ", line.strip())
    if not header:
        return False
    if _looks_like_date_line(header):
        return True
    upper = header.upper().rstrip(".,;:!?")
    weekday_prefixes = (
        "MONDAY",
        "TUESDAY",
        "WEDNESDAY",
        "THURSDAY",
        "FRIDAY",
        "SATURDAY",
        "SUNDAY",
    )
    if upper.startswith(weekday_prefixes):
        return True
    if len(header) <= 80 and _is_uppercaseish(header):
        return True
    return False



def _looks_like_salutation_line(line: str) -> bool:
    header = re.sub(r"\s+", " ", line.strip())
    upper = header.upper()
    if not header.endswith((",", "!")):
        return False
    if upper in {"MADAM,", "MADAM!", "SIR,", "SIR!"}:
        return True
    salutation_prefixes = (
        "DEAR ",
        "MY DEAR ",
        "MY DEAREST ",
        "O MY DEAR ",
        "O MY DEAREST ",
    )
    return upper.startswith(salutation_prefixes) and (_is_uppercaseish(header) or header[0].isupper())


ITALIC_SALUTATION_WITH_BODY_RE = re.compile(r"^_(.+?:)_\s*(.*)$")


def _split_italic_salutation_paragraph(paragraph: str) -> tuple[str, str] | None:
    match = ITALIC_SALUTATION_WITH_BODY_RE.match(paragraph.strip())
    if not match:
        return None
    title = match.group(1).strip()
    remainder = match.group(2).strip()
    return title, remainder


def _split_plain_salutation_paragraph(paragraph: str) -> tuple[str, str] | None:
    stripped = re.sub(r"\s+", " ", paragraph.strip())
    for marker in (",", "!"):
        split_at = stripped.find(marker)
        if split_at == -1:
            continue
        title = stripped[: split_at + 1].strip()
        remainder = stripped[split_at + 1 :].strip()
        if remainder and _looks_like_salutation_line(title):
            return title, remainder
    return None



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



def _looks_like_mixed_case_to_header(line: str) -> bool:
    upper = line.upper()
    if " TO " not in upper:
        return False
    split_at = upper.index(" TO ")
    left = line[:split_at].strip()
    right = line[split_at + 4 :].strip()
    return bool(left and right and _is_uppercaseish(left) and any(ch.isalpha() for ch in right) and right[0].isupper())



def _looks_like_mixed_case_continuation_header(line: str) -> bool:
    upper = line.upper()
    marker = " IN CONTINUATION"
    if marker not in upper:
        return False
    prefix = line[: upper.index(marker)].strip()
    return bool(prefix and _is_uppercaseish(prefix))


def _normalize_italic_correspondent_title(line: str) -> str:
    title = line.strip()
    if not title:
        return title
    title = re.sub(r"_([^_]+)_", r"\1", title)
    return re.sub(r"\s+", " ", title).strip()


def _looks_like_italic_correspondent_header(line: str) -> bool:
    stripped = line.strip()
    if "_" not in stripped or " to " not in stripped.lower():
        return False
    normalized = _normalize_italic_correspondent_title(stripped)
    upper = normalized.upper()
    if upper.startswith("FROM "):
        return True
    if " TO " not in upper:
        return False
    left, right = normalized.split(" to ", 1)
    left = left.strip(' .,_;:-')
    right = right.strip()
    return bool(left and right and left[0].isupper() and any(ch.isalpha() for ch in right) and right[0].isupper())


LETTER_HEADING_RE = re.compile(r"LETTER\s+([IVXLCDM]+|THE\s+[A-Z-]+)\.?(?:\s+(.*))?$", re.IGNORECASE)

SPELLED_ORDINAL_TO_ROMAN = {
    "THE FIRST": "I",
    "THE SECOND": "II",
    "THE THIRD": "III",
    "THE FOURTH": "IV",
    "THE FIFTH": "V",
    "THE SIXTH": "VI",
    "THE SEVENTH": "VII",
    "THE EIGHTH": "VIII",
    "THE NINTH": "IX",
    "THE TENTH": "X",
    "THE ELEVENTH": "XI",
    "THE TWELFTH": "XII",
    "THE THIRTEENTH": "XIII",
    "THE FOURTEENTH": "XIV",
    "THE FIFTEENTH": "XV",
    "THE SIXTEENTH": "XVI",
    "THE SEVENTEENTH": "XVII",
    "THE EIGHTEENTH": "XVIII",
    "THE NINETEENTH": "XIX",
    "THE TWENTIETH": "XX",
}


def _normalize_letter_heading_label(raw_label: str) -> str | None:
    normalized = re.sub(r"\s+", " ", raw_label.strip()).upper()
    if re.fullmatch(r"[IVXLCDM]+", normalized):
        return normalized
    return SPELLED_ORDINAL_TO_ROMAN.get(normalized)


def _parse_letter_heading_line(line: str) -> tuple[str, str, str] | None:
    stripped = line.strip()
    if not stripped.startswith(("LETTER ", "Letter ")):
        return None

    match = LETTER_HEADING_RE.fullmatch(stripped)
    if not match:
        return None

    label = _normalize_letter_heading_label(match.group(1))
    if not label:
        return None
    remainder = (match.group(2) or "").strip()
    if not remainder:
        return label, "", ""

    notes = re.findall(r"\[[^\]]+\]", remainder)
    heading_note = " ".join(notes)
    inline_title = re.sub(r"\s*\[[^\]]+\]\s*", " ", remainder).strip()
    inline_title = re.sub(r"\s+", " ", inline_title)
    if inline_title and not inline_title[0].isupper():
        return None
    return label, heading_note, inline_title


LEADING_MONTH_DATE_RE = re.compile(
    r"^((?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:t(?:ember)?)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{1,2}(?:st|nd|rd|th)?[.,-]?)\s+(.+)$",
    re.IGNORECASE,
)


def _looks_like_correspondent_header(lines: list[str]) -> bool:
    if not lines:
        return False

    first = lines[0].strip()
    first_upper = first.upper()
    if (
        (first_upper.startswith("TO ") and len(first) > 3 and first[3].isupper())
        or first_upper.startswith("FROM ")
        or _looks_like_mixed_case_to_header(first)
        or _looks_like_italic_correspondent_header(first)
        or ((_is_uppercaseish(first) and " FROM " in first_upper))
        or _looks_like_mixed_case_continuation_header(first)
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



def _split_inline_continuation_body(title_text: str) -> tuple[str, str]:
    upper = title_text.upper()
    marker = " IN CONTINUATION"
    if marker not in upper:
        return title_text, ""

    split_at = upper.index(marker) + len(marker)
    remainder = title_text[split_at:].strip()
    if not remainder:
        return title_text, ""

    first_chunk = remainder[:40]
    first_word = remainder.split()[0].strip('.,;:!?"\'').upper()
    if any(ch.isdigit() for ch in remainder) or "," in first_chunk:
        return title_text, ""
    if first_word not in {"I", "THIS", "MY", "WE", "HE", "SHE", "THEY", "IT", "BUT", "AND", "DEAR"}:
        return title_text, ""

    return title_text[:split_at].strip(), remainder



def _split_leading_date_paragraph(paragraph: str) -> tuple[str, str] | None:
    match = LEADING_MONTH_DATE_RE.match(paragraph.strip())
    if not match:
        return None
    subtitle = match.group(1).strip()
    remainder = match.group(2).strip()
    if not remainder:
        return None
    return subtitle, remainder



def _looks_like_letter_heading(lines: list[str], index: int) -> bool:
    parsed = _parse_letter_heading_line(lines[index])
    if not parsed:
        return False

    _, _, inline_title = parsed
    if inline_title:
        return True

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
    paras: list[str], fallback_label: str, global_title: str | None = None, inline_title: str = ""
) -> tuple[str, str, list[str]]:
    if inline_title:
        subtitle = ""
        body_start = 0
        if paras and _looks_like_date_line(paras[0]):
            split_date_paragraph = _split_leading_date_paragraph(paras[0])
            if split_date_paragraph:
                subtitle, inline_dated_body = split_date_paragraph
                return inline_title, subtitle, [inline_dated_body] + paras[1:]
            subtitle = paras[0]
            body_start = 1
        return inline_title, subtitle, paras[body_start:]

    if not paras:
        return global_title or f"Letter {fallback_label}", "", []

    if global_title and not _looks_like_correspondent_header(paras[:3]):
        return global_title, "", paras

    title_text = paras[0]
    if _looks_like_italic_correspondent_header(title_text):
        title_text = _normalize_italic_correspondent_title(title_text)
    body_start = 1
    subtitle = ""
    body_prefix: list[str] = []

    plain_salutation_split = _split_plain_salutation_paragraph(title_text)
    if plain_salutation_split:
        title_text, inline_body = plain_salutation_split
        body_prefix.append(inline_body)

    if len(paras) > 1 and (
        paras[1].upper().startswith("[IN ") or paras[1].upper().startswith("[ENCLOSED ")
    ):
        title_text = f"{title_text} {paras[1]}"
        body_start = 2

    title_text, inline_body = _split_inline_continuation_body(title_text)
    if inline_body:
        body_prefix.append(inline_body)

    if len(paras) > body_start and _looks_like_date_line(paras[body_start]):
        split_date_paragraph = _split_leading_date_paragraph(paras[body_start])
        if split_date_paragraph:
            subtitle, inline_dated_body = split_date_paragraph
            body_prefix.append(inline_dated_body)
        else:
            subtitle = paras[body_start]
        body_start += 1
    elif title_text.upper().startswith("[IN ") or title_text.upper().startswith("[ENCLOSED "):
        if len(paras) > body_start and _looks_like_salutation_line(paras[body_start]):
            subtitle = paras[body_start]
            body_start += 1

    return title_text, subtitle, body_prefix + paras[body_start:]



def _disambiguate_section_id(base_id: str, seen_ids: dict[str, int]) -> str:
    count = seen_ids.get(base_id, 0) + 1
    seen_ids[base_id] = count
    if count == 1:
        return base_id
    return f"{base_id}-{count}"


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

    headings: list[tuple[int, str, str, str]] = []
    if heading_mode == "roman":
        for i in range(start_idx, len(lines)):
            s = lines[i].strip()
            if _looks_like_roman_epistolary_heading(lines, i):
                headings.append((i, s, "", ""))
            elif s == "CONCLUSION":
                headings.append((i, s, "", ""))
    elif heading_mode == "letter-heading":
        for i in range(start_idx, len(lines)):
            parsed = _parse_letter_heading_line(lines[i])
            if _looks_like_letter_heading(lines, i) and parsed:
                label, heading_note, inline_title = parsed
                headings.append((i, label, heading_note, inline_title))
    else:
        for i in range(start_idx, len(lines)):
            if _looks_like_to_line_heading(lines, i):
                headings.append((i, str(len(headings) + 1), "", ""))

    sections: list[Section] = []
    seen_ids: dict[str, int] = {}
    for index, (line_no, label, heading_note, inline_title) in enumerate(headings):
        end = headings[index + 1][0] if index + 1 < len(headings) else len(lines)
        chunk_lines = [line.rstrip() for line in lines[line_no:end]]
        raw_body = "\n".join(chunk_lines[1:]).strip()
        paras = _paragraphize(raw_body)

        if heading_mode == "roman":
            if paras and paras[0].startswith("_") and paras[0].endswith("_"):
                title_text = paras[0].strip("_")
                body = paras[1:]
                subtitle = body[0] if body and len(body[0]) < 80 else ""
                if subtitle:
                    body = body[1:]
            elif paras and _looks_like_correspondent_header(paras[:3]):
                title_text = paras[0]
                subtitle_parts: list[str] = []
                body_start = 1
                while body_start < len(paras) and _looks_like_brief_dateline_line(paras[body_start]):
                    subtitle_parts.append(paras[body_start])
                    body_start += 1
                subtitle = " ".join(subtitle_parts)
                body = paras[body_start:]
            elif len(paras) >= 2 and _looks_like_date_line(paras[0]):
                salutation_split = _split_italic_salutation_paragraph(paras[1])
                if salutation_split:
                    title_text, inline_body = salutation_split
                    subtitle = paras[0]
                    body = ([inline_body] if inline_body else []) + paras[2:]
                else:
                    title_text = "Conclusion"
                    subtitle = paras[0] if paras and len(paras[0]) < 80 else ""
                    body = paras[1:] if subtitle else paras
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
                paras, label, _extract_global_correspondent_title(lines, line_no), inline_title=inline_title
            )
            if heading_note:
                title_text = f"{title_text} {heading_note}".strip()
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
                id=_disambiguate_section_id(sec_id, seen_ids),
                order=index + 1,
                label=sec_label,
                title=title_text,
                subtitle=subtitle,
                body=body,
            )
        )
    return sections
