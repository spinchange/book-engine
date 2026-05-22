from __future__ import annotations

import re
import unicodedata
from pathlib import Path

from ..models import Section
from .gutenberg_txt import extract_source_main_text


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


def _parse_heading(line: str) -> tuple[str, str, str, bool] | None:
    stripped = line.strip()
    upper = stripped.upper()

    for prefix, kind, readable_prefix in (
        ("CHAPTER ", "chapter", "Chapter"),
        ("BOOK ", "book", "Book"),
        ("PART ", "part", "Part"),
        ("LETTER ", "letter", "Letter"),
    ):
        if not upper.startswith(prefix):
            continue

        remainder = stripped[len(prefix) :]
        match = re.match(r"([IVXLCDM]+|\d+)(.*)$", remainder, re.IGNORECASE)
        if not match:
            return None

        numeral = match.group(1).upper()
        trailing = match.group(2).strip()
        inline_title = trailing.lstrip(".:-— ").strip()
        title_from_following_block = stripped[: len(prefix)].isupper()
        return kind, f"{readable_prefix} {numeral}", inline_title, title_from_following_block

    if upper.startswith("CHAPITRE "):
        remainder = stripped[len("CHAPITRE ") :]
        match = re.match(r"(PREMIER|[IVXLCDM]+|\d+)(.*)$", remainder, re.IGNORECASE)
        if not match:
            return None
        numeral_token = match.group(1)
        numeral = numeral_token.title() if numeral_token.upper() == "PREMIER" else numeral_token.upper()
        trailing = match.group(2).strip()
        inline_title = trailing.lstrip(".:-— ").strip()
        title_from_following_block = stripped[: len("CHAPITRE ")].isupper()
        return "chapitre", f"Chapitre {numeral}", inline_title, title_from_following_block

    if re.fullmatch(r"THE EDITOR TO THE READER\.?", stripped):
        return "editorial", "THE EDITOR TO THE READER", "", False

    if stripped == "LETTRE À L'ÉDITEUR":
        return "editorial-letter", "Lettre à l'éditeur", "", False

    if stripped == "RÉPONSE.":
        return "response", "Réponse", "", False

    return None



def _line_starts_heading(line: str) -> bool:
    return _parse_heading(line) is not None



def _slugify_label(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", "-", normalized.lower()).strip("-")



def _looks_like_short_date_heading(text: str) -> bool:
    cleaned = text.strip().rstrip(".")
    if not cleaned:
        return False

    month_match = re.fullmatch(
        r"(?:JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|AUGUST|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER)\s+\d{1,2}(?:,\s*\d{4})?",
        cleaned,
    )
    weekday_match = re.fullmatch(
        r"(?:MONDAY|TUESDAY|WEDNESDAY|THURSDAY|FRIDAY|SATURDAY|SUNDAY),\s+\d{1,2}(?:\s+[A-Z]+)*",
        cleaned,
    )
    return bool(month_match or weekday_match)


MONTH_TOKEN_RE = re.compile(
    r"\b(?:JAN(?:UARY)?|FEB(?:RUARY)?|MAR(?:CH)?|APR(?:IL)?|MAY|JUN(?:E)?|JUL(?:Y)?|AUG(?:UST)?|SEP(?:T(?:EMBER)?)?|OCT(?:OBER)?|NOV(?:EMBER)?|DEC(?:EMBER)?)\b",
    re.IGNORECASE,
)


def _looks_like_letter_dateline(text: str) -> bool:
    cleaned = text.strip()
    return bool(cleaned and MONTH_TOKEN_RE.search(cleaned) and any(ch.isdigit() for ch in cleaned))


def _looks_like_body_opening_paragraph(text: str, line_count: int = 1) -> bool:
    cleaned = text.strip()
    words = cleaned.split()
    if not cleaned.endswith((".", "!", "?")):
        return False
    if line_count == 1:
        return True
    first_word = words[0].strip('“"\'"').upper() if words else ""
    if first_word in {"I", "WE", "HE", "SHE", "THEY", "IT", "THIS", "THAT", "THERE", "AS"}:
        return len(words) >= 10
    return False


def _looks_like_short_chapter_title(text: str) -> bool:
    cleaned = text.strip()
    if not cleaned or cleaned.endswith((".", "!", "?")):
        return False
    words = cleaned.split()
    if len(words) > 8:
        return False
    alpha_words = [word for word in words if any(ch.isalpha() for ch in word)]
    if not alpha_words:
        return False
    return all(next((ch for ch in word if ch.isalpha()), "").isupper() for word in alpha_words)


def _normalize_heading_comparison(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text)
    return "".join(ch.casefold() for ch in normalized if ch.isalnum())


def _consume_repeated_documentary_heading(chunk_lines: list[str], title_text: str) -> list[str]:
    probe_index = 0
    while probe_index < len(chunk_lines) and not chunk_lines[probe_index].strip():
        probe_index += 1
    if probe_index >= len(chunk_lines):
        return chunk_lines

    candidate = chunk_lines[probe_index].strip().strip("_")
    if _normalize_heading_comparison(candidate) != _normalize_heading_comparison(title_text):
        return chunk_lines

    remainder = chunk_lines[probe_index + 1 :]
    while remainder and not remainder[0].strip():
        remainder.pop(0)
    return remainder


def _collect_wrapped_heading_title(lines: list[str], start_index: int, inline_title: str) -> str:
    title_parts: list[str] = []
    if inline_title:
        title_parts.append(inline_title)

    probe_index = start_index + 1
    while probe_index < len(lines):
        candidate = lines[probe_index].strip()
        if not candidate or _line_starts_heading(candidate):
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
        if _line_starts_heading(candidate):
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


def parse_chaptered_text(
    source_path: Path, title: str, source_format: str = "gutenberg-txt"
) -> list[Section]:
    text = source_path.read_text(encoding="utf-8", errors="replace")
    main_text = extract_source_main_text(text, title, source_format=source_format)
    lines = [line.rstrip() for line in main_text.split("\n")]

    headings: list[tuple[int, str, str, str, bool]] = []
    toc_titles: dict[str, str] = {}
    for index, line in enumerate(lines):
        parsed = _parse_heading(line)
        if not parsed:
            continue
        kind, label, inline_title, title_from_following_block = parsed
        headings.append((index, kind, label, inline_title, title_from_following_block))
        if kind in {"chapter", "chapitre"} and inline_title and label not in toc_titles:
            toc_titles[label] = _collect_wrapped_heading_title(lines, index, inline_title)

    if not headings:
        raise RuntimeError("Could not locate any chapter headings")

    deduped_reversed: list[tuple[int, str, str, str, bool]] = []
    seen_labels: set[tuple[str, str]] = set()
    for heading in reversed(headings):
        _, kind, label, _, _ = heading
        heading_key = (kind, label)
        if heading_key in seen_labels:
            continue
        seen_labels.add(heading_key)
        deduped_reversed.append(heading)
    headings = list(reversed(deduped_reversed))

    sections: list[Section] = []
    for order, (start_index, kind, label, inline_title, title_from_following_block) in enumerate(headings, start=1):
        end_index = headings[order][0] if order < len(headings) else len(lines)
        chunk_lines = lines[start_index + 1 : end_index]

        title_parts: list[str] = []
        subtitle = ""
        if kind in {"chapter", "chapitre"} and inline_title:
            title_parts.append(inline_title)
            while chunk_lines and not chunk_lines[0].strip():
                chunk_lines.pop(0)
            while chunk_lines and chunk_lines[0].strip():
                title_parts.append(chunk_lines.pop(0).strip())
            while chunk_lines and not chunk_lines[0].strip():
                chunk_lines.pop(0)
        elif kind == "chapter":
            while chunk_lines and not chunk_lines[0].strip():
                chunk_lines.pop(0)
            if label in toc_titles:
                title_parts.append(toc_titles[label])
            elif title_from_following_block:
                sparse_wrapped_title = _consume_sparse_wrapped_title_block(chunk_lines)
                if sparse_wrapped_title is not None:
                    candidate_title_parts, candidate_remainder = sparse_wrapped_title
                    candidate_title = re.sub(r"\s+", " ", " ".join(candidate_title_parts)).strip()
                    if not _looks_like_body_opening_paragraph(candidate_title, line_count=len(candidate_title_parts)):
                        title_parts, chunk_lines = candidate_title_parts, candidate_remainder
                elif chunk_lines and chunk_lines[0].strip():
                    probe_index = 0
                    candidate_lines: list[str] = []
                    while probe_index < len(chunk_lines) and chunk_lines[probe_index].strip():
                        candidate_lines.append(chunk_lines[probe_index].strip())
                        probe_index += 1
                    candidate_title = re.sub(r"\s+", " ", " ".join(candidate_lines)).strip()
                    if not _looks_like_body_opening_paragraph(candidate_title, line_count=len(candidate_lines)):
                        title_parts.extend(candidate_lines)
                        chunk_lines = chunk_lines[probe_index:]
                elif chunk_lines and _looks_like_short_chapter_title(chunk_lines[0].strip()):
                    title_parts.append(chunk_lines.pop(0).strip())
                while chunk_lines and not chunk_lines[0].strip():
                    chunk_lines.pop(0)
            elif chunk_lines and _looks_like_short_chapter_title(chunk_lines[0].strip()):
                title_parts.append(chunk_lines.pop(0).strip())
                while chunk_lines and not chunk_lines[0].strip():
                    chunk_lines.pop(0)
        elif kind == "chapitre":
            while chunk_lines and not chunk_lines[0].strip():
                chunk_lines.pop(0)
            if label in toc_titles:
                title_parts.append(toc_titles[label])
        elif kind == "part":
            while chunk_lines and not chunk_lines[0].strip():
                chunk_lines.pop(0)
            sparse_wrapped_title = _consume_sparse_wrapped_title_block(chunk_lines)
            if sparse_wrapped_title is not None:
                title_parts, chunk_lines = sparse_wrapped_title
            elif chunk_lines and chunk_lines[0].strip():
                while chunk_lines and chunk_lines[0].strip():
                    title_parts.append(chunk_lines.pop(0).strip())
                while chunk_lines and not chunk_lines[0].strip():
                    chunk_lines.pop(0)
        elif kind == "letter":
            while chunk_lines and not chunk_lines[0].strip():
                chunk_lines.pop(0)
            if chunk_lines and chunk_lines[0].strip().startswith("_") and chunk_lines[0].strip().endswith("_"):
                title_parts.append(chunk_lines.pop(0).strip().strip("_"))
                while chunk_lines and not chunk_lines[0].strip():
                    chunk_lines.pop(0)
            if chunk_lines and _looks_like_letter_dateline(chunk_lines[0].strip()):
                subtitle = chunk_lines.pop(0).strip()
                while chunk_lines and not chunk_lines[0].strip():
                    chunk_lines.pop(0)

        else:
            while chunk_lines and not chunk_lines[0].strip():
                chunk_lines.pop(0)

        raw_body = "\n".join(chunk_lines).strip()
        body = _paragraphize(raw_body)

        if kind == "chapter":
            section_id = _slugify_label(label)
            readable_label = f"Chapter {label.split(maxsplit=1)[1]}"
            title_line = re.sub(r"\s+", " ", " ".join(title_parts)).strip() or readable_label
            if label in toc_titles:
                chunk_lines = _consume_repeated_documentary_heading(chunk_lines, title_line)
                raw_body = "\n".join(chunk_lines).strip()
                body = _paragraphize(raw_body)
        elif kind == "chapitre":
            section_id = _slugify_label(label)
            readable_label = label
            title_line = re.sub(r"\s+", " ", " ".join(title_parts)).strip() or readable_label
        elif kind == "book":
            section_id = _slugify_label(label)
            readable_label = f"Book {label.split(maxsplit=1)[1]}"
            title_line = readable_label
            if body and _looks_like_short_date_heading(body[0].upper()):
                subtitle = body[0]
                body = body[1:]
        elif kind == "part":
            section_id = _slugify_label(label)
            readable_label = f"Part {label.split(maxsplit=1)[1]}"
            title_line = re.sub(r"\s+", " ", " ".join(title_parts)).strip() or readable_label
        elif kind == "letter":
            section_id = _slugify_label(label)
            readable_label = label
            title_line = re.sub(r"\s+", " ", " ".join(title_parts)).strip() or readable_label
        elif kind == "editorial":
            section_id = _slugify_label(label)
            readable_label = "Editor"
            title_line = "The Editor to the Reader"
        else:
            section_id = _slugify_label(label)
            readable_label = label
            title_line = label

        sections.append(
            Section(
                id=section_id,
                order=order,
                label=readable_label,
                title=title_line or readable_label,
                subtitle=subtitle,
                body=body,
            )
        )

    return sections
