#! /usr/bin/env python3
import os
import time
import shutil
import argparse

from lib.create_abstract_tree import VirtualFS

from lib.settings import settings
from lib.thumb_cache import ThumbCache
from lib.preprocessors import get_preprocessors
from lib.postprocessors import get_postprocessors
from lib.html_transformers import get_transformers
from lib.html_transformers.generate_thumbnails import GenerateThumbnails


def generate_blog(zipfile, blog_root):
    start_ts = time.time()

    GenerateThumbnails.thumb_cache = ThumbCache.create_thumb_cache(blog_root)

    _make_directory_empty(blog_root)

    blog_tree = VirtualFS(zipfile)

    root_node = blog_tree.root
    _run_preprocessors(blog_tree, root_node)
    _run_html_transformers(blog_tree, root_node)
    _run_postprocessors(blog_tree, root_node)

    blog_tree.store_on_disc(blog_root)

    settings.logger.info("Blog generated in %.2f seconds.",
                         time.time() - start_ts)


def _run_preprocessors(blog_tree, root_node):
    for preprocessor in get_preprocessors():
        preprocessor.preprocess(blog_tree, root_node)


def _run_html_transformers(blog_tree, root_node):
    for transformer in get_transformers():
        transformer.log_transformer()

        for html_file in root_node.walk_htmls():
            transformer.transform(blog_tree, root_node, html_file)


def _run_postprocessors(blog_tree, root_node):
    for postprocessor in get_postprocessors():
        postprocessor.postprocess(blog_tree, root_node)


def _make_directory_empty(blog_path):
    if os.path.exists(blog_path) and "index.html" in os.listdir(blog_path):
        for item in os.listdir(blog_path):
            if item == ".git":
                continue

            path = os.path.join(blog_path, item)

            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.unlink(path)

    os.makedirs(blog_path, exist_ok=True)


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
