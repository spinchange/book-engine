from __future__ import annotations

import argparse
from pathlib import Path

from .builder import build_library


def main() -> None:
    parser = argparse.ArgumentParser(prog="book-engine", description="Build a content repo into a static HTML library site.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    build_parser = subparsers.add_parser("build", help="Build a content repo into static HTML")
    build_parser.add_argument("content_root", help="Path to the content repo root")
    build_parser.add_argument("--output", help="Optional output directory override")

    args = parser.parse_args()

    if args.command == "build":
        output = build_library(Path(args.content_root), Path(args.output) if args.output else None)
        print(output)


if __name__ == "__main__":
    main()
