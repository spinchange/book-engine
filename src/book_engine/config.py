from __future__ import annotations

from pathlib import Path
import yaml

from .models import BookConfig


def load_yaml(path: Path) -> dict:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise ValueError(f"Expected mapping in {path}")
    return data


def load_library_config(root: Path) -> dict:
    data = load_yaml(root / "library.yaml")
    data.setdefault("books_dir", "books")
    data.setdefault("output_dir", "dist")
    data.setdefault("default_theme", "classic-paper")
    data.setdefault("base_url", "")
    return data


def load_book_config(path: Path) -> BookConfig:
    data = load_yaml(path)
    return BookConfig(
        id=data["id"],
        title=data["title"],
        author=data.get("author", "Unknown"),
        year=str(data.get("year", "")),
        source_file=data.get("source_file", "source.txt"),
        source_format=data.get("source_format", "gutenberg-txt"),
        profile=data.get("profile", "epistolary"),
        parser=data.get("parser", "gutenberg-letters-v1"),
        theme=data.get("theme", "classic-paper"),
        source_url=data.get("source_url", ""),
        description=data.get("description", ""),
    )
