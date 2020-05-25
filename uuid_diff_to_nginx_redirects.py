#! /usr/bin/env python3
import sys
import os
import os.path
import hashlib
import argparse

from lib.virtual_fs import HtmlPage

import tqdm


def do_diff_and_print_redirects(old_dir, new_dir):
    hash_to_blog_path_old = _generate_hash_to_blog_map(old_dir)
    hash_to_blog_path_new = _generate_hash_to_blog_map(new_dir)

    for hash, new_path in hash_to_blog_path_new.items():
        old_path = hash_to_blog_path_old.get(hash)

        if old_path is None:
            continue

        if old_path == new_path:
            continue

        _print_as_nginx_redirect(old_path, new_path)


def _generate_hash_to_blog_map(old_dir):
    hash_to_blog_path = {}
    for path, blog_path in tqdm.tqdm(list(_walk_blog(old_dir))):
        if path.endswith(".html"):
            hash = _get_html_content_independent_hash(path)
        else:
            hash = _get_file_hash(path)

        hash_to_blog_path[hash] = blog_path

    return hash_to_blog_path


def _walk_blog(blog_dir):
    for root, dirs, files in os.walk(blog_dir):
        for file in files:
            if "/.git" in root:
                continue
            if "/.idea" in root:
                continue

            path = os.path.join(root, file)

            abs_blog = os.path.abspath(blog_dir)
            blog_path = os.path.abspath(path).replace(abs_blog, "")

            yield path, blog_path


def _get_html_content_independent_hash(path):
    with open(path) as f:
        page = HtmlPage(f.read(), path)

    article_tags = page.dom.find("article")
    if article_tags:
        id = article_tags[0].params.get("id")
        if id:
            return id

    return page.dom.find("h1", {"class": "page-title"})[0].__str__()


def _get_file_hash(path):
    with open(path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()


def _print_as_nginx_redirect(old_path, new_path):
    template = """location '%s' {
    return 301 '%s';
}"""

    print(template % (old_path, new_path))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-o",
        "--old-structure",
        required=True,
        help="Old structure you want to diff with new one."
    )
    parser.add_argument(
        "-n",
        "--new-structure",
        required=True,
        help="New structure of the blog."
    )

    args = parser.parse_args()

    if not os.path.exists(args.old_structure) or not os.path.isdir(args.old_structure):
        sys.stderr.write("--old-structure does not exist!\n")
        sys.exit(1)

    if not os.path.exists(args.new_structure) or not os.path.isdir(args.new_structure):
        sys.stderr.write("--new-structure does not exist!\n")
        sys.exit(1)

    do_diff_and_print_redirects(args.old_structure, args.new_structure)
