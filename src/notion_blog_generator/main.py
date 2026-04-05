import argparse

from notion_blog_generator.settings import settings
from notion_blog_generator.generator import BlogGenerator


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

    generator = BlogGenerator(args.zipfile, args.blogroot)
    generator.generate_blog()


if __name__ == '__main__':
    main()
