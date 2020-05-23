#! /usr/bin/env python3
import os
import shutil
import argparse

from lib.create_abstract_tree import VirtualFS

from lib.preprocessors import get_preprocessors
from lib.html_transformers import get_transformers


def generate_blog(zipfile, blog_root):
    # thumb_cache = ThumbCache.create_thumb_cache(blog_root)
    empty_directory(blog_root)

    blog_tree = VirtualFS(zipfile)

    root_node = blog_tree.root
    for preprocessor in get_preprocessors():
        preprocessor.preprocess(blog_tree, root_node)

    for transformer in get_transformers():
        transformer.log_transformer()

        for html_file in root_node.walk_htmls():
            transformer.transform(blog_tree, root_node, html_file)

    blog_tree.store_on_disc(blog_root)


def empty_directory(blog_path):
    if os.path.exists(blog_path):
        for item in os.listdir(blog_path):
            if item == ".git":
                continue

            path = os.path.join(blog_path, item)

            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.unlink(path)

    os.makedirs(blog_path, exist_ok=True)


# def _copy_to(copy_from, copy_to):
#     if os.path.isdir(copy_from):
#         shutil.copytree(os.path.join(os.path.dirname(__file__), copy_from), copy_to)
#     else:
#         shutil.copy(os.path.join(os.path.dirname(__file__), copy_from), copy_to)
#
#
# def _save_unpacked_data(blog_root, filename, data):
#     full_path = os.path.join(blog_root, filename)
#     dir_path = os.path.dirname(full_path)
#
#     os.makedirs(dir_path, exist_ok=True)
#
#     with open(full_path, "wb") as f:
#         f.write(data)
#
#
# def _get_real_blog_root(blog_root):
#     for path in os.listdir(blog_root):
#         full_path = os.path.join(blog_root, path)
#         if os.path.isdir(full_path):
#             return full_path
#
#     raise ValueError("Real blogroot not found!")
#
#
# def postprocess_all_html_pages(shared_resources, blog_root):
#     for path, page in shared_resources.all_pages.items():
#         page.transform()
#
#     AddSidebar.add_to_all_relevant_pages()
#
#     for path, page in shared_resources.all_pages.items():
#         page.save(blog_root)


if __name__ == '__main__':
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

    args = parser.parse_args()

    generate_blog(args.zipfile, args.blogroot)
