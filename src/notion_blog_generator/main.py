#! /usr/bin/env python3
import argparse
from pathlib import Path

from notion_blog_generator.settings import settings
from notion_blog_generator.generator import BlogGenerator


def _path_or_find_zipfile_if_dir(path_str: str) -> str:
    path = Path(path_str)

    if not path.is_dir():
        return path_str

    for zipfile in path.glob("*-*-*.zip"):
        return str(zipfile)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        "--zipfile",
        help="Path to the export zipfile."
    )
    parser.add_argument(
        "-o",
        "--blogroot",
        help="Path to the blog directory / git repo."
    )
    parser.add_argument(
        "--no-thumbs",
        action="store_true",
        help="Don't generate thumbnails (much faster)."
    )

    args = parser.parse_args()

    if args.no_thumbs:
        settings.generate_thumbnails = False

    zipfile = _path_or_find_zipfile_if_dir(args.zipfile)

    generator = BlogGenerator(zipfile, args.blogroot)
    generator.generate_blog()


if __name__ == '__main__':
    main()
