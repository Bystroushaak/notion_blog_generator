#! /usr/bin/env python3
import sys
import os
import os.path
import argparse

import sh
import tqdm


def generate_font_subset(blogroot, font_path):
    unicode_characters = set()
    for path in tqdm.tqdm(list(_walk_html_files_in_blog(blogroot))):
        with open(path, "rb") as f:
            data = f.read().decode("utf-8")

        for char in data:
            if ord(char) > 1000:
                unicode_characters.add(char)

    unicode_points = ",".join(_convert_unicode_chars_to_codepoints(unicode_characters))

    pyftsubset = sh.Command("~/.local/bin/pyftsubset")

    pyftsubset(font_path, unicodes=unicode_points, layout_features="",
               output_file="static_files/NotoEmojiSubset.ttf", )
    pyftsubset(font_path, unicodes=unicode_points, layout_features="",
               output_file="static_files/NotoEmojiSubset.woff", )

    print("Updated font files saved to static_files/.")


def _convert_unicode_chars_to_codepoints(unicode_characters):
    for char in sorted(unicode_characters):
        encoded = char.encode("unicode_escape")
        # if b"U" not in encoded:
        #     continue

        print(char, end=" ")
        

        yield encoded.replace(b"\\U", b"U+").decode("utf-8")

    print()


def _walk_html_files_in_blog(blog_dir):
    for root, dirs, files in os.walk(blog_dir):
        for file in files:
            if "/.git" in root:
                continue
            if "/.idea" in root:
                continue

            if not file.endswith(".html"):
                continue

            yield os.path.join(root, file)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "BLOGROOT",
        help="Path to the generated blog."
    )
    parser.add_argument(
        "-f",
        "--font",
        default="resources/NotoColorEmoji.ttf",
        help="Path to the font. Default %(default)s."
    )
    args = parser.parse_args()

    if not os.path.exists(args.BLOGROOT):
        sys.stderr.write("Blogroot `%s` not found.\n" % args.BLOGROOT)
        sys.exit(1)

    if not os.path.exists(args.font):
        sys.stderr.write("Font `%s` not found.\n" % args.font)
        sys.exit(1)


    generate_font_subset(args.BLOGROOT, args.font)
