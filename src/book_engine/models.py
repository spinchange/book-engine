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
    kind: str = "section"
    body_format: str = "plain"


@dataclass
class FrontMatterConfig:
    id: str
    title: str
    source_file: str
    source_format: str = "markdown"


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
    front_matter: list[FrontMatterConfig] = field(default_factory=list)


@dataclass
class Book:
    config: BookConfig
    root: Path
    sections: list[Section] = field(default_factory=list)

    @property
    def output_slug(self) -> str:
        return self.config.id
