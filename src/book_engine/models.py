from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Section:
    id: str
    order: int
    label: str
    title: str
    subtitle: str
    body: list[str]


@dataclass
class BookConfig:
    id: str
    title: str
    author: str
    year: str
    source_file: str
    source_format: str
    profile: str
    parser: str
    theme: str
    source_url: str = ""
    description: str = ""


@dataclass
class Book:
    config: BookConfig
    root: Path
    sections: list[Section] = field(default_factory=list)

    @property
    def output_slug(self) -> str:
        return self.config.id
