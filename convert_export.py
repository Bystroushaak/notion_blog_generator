#! /usr/bin/env python3
import os
import shutil
import os.path
import zipfile
import argparse

from lib.postprocessors.generate_nice_filenames import empty_directory
from lib.postprocessors.generate_nice_filenames import fix_filenames_and_generate_new_structure

from lib.shared_resources import SharedResources
from lib.page import Page
from lib.transformers import AddSidebar
from lib.thumb_cache import ThumbCache


def generate_blog(zipfile, blog_root):
    thumb_cache = ThumbCache.create_thumb_cache(blog_root)
    empty_directory(blog_root)

    shared_resources = SharedResources(blog_root)

    for zf, item in iterate_zipfile(zipfile):
        if item.filename.endswith(".html"):
            page = Page(item.filename, zf.read(item).decode("utf-8"),
                        shared_resources)
            shared_resources.add_page(item.filename, page)
            print(item.filename, "extracted and stored for postprocessing")
        else:
            zf.extract(item, path=blog_root)
            print(item.filename, "extracted")

    real_blog_root = _get_real_blog_root(blog_root)
    shared_resources._real_blog_root = real_blog_root
    shared_resources.generate_title_map()
    shared_resources.thumb_cache = thumb_cache

    postprocess_all_html_pages(shared_resources, blog_root)

    print("Saving all pages..")
    shared_resources.save()

    shutil.copy(os.path.join(os.path.dirname(__file__), "icons/favicon.ico"), real_blog_root)
    shutil.copy(os.path.join(os.path.dirname(__file__), "tweet_button.svg"), real_blog_root)
    shutil.copy(os.path.join(os.path.dirname(__file__), "scripts.js"), real_blog_root)
    shutil.copytree(os.path.join(os.path.dirname(__file__), "icons"), real_blog_root + "/icons")

    fix_filenames_and_generate_new_structure(blog_root, real_blog_root)


def _get_real_blog_root(blog_root):
    for path in os.listdir(blog_root):
        full_path = os.path.join(blog_root, path)
        if os.path.isdir(full_path):
            return full_path

    raise ValueError("Real blogroot not found!")


def iterate_zipfile(zipfile_path):
    zf = zipfile.ZipFile(zipfile_path)

    for zip_info in zf.infolist():
        yield zf, zip_info

    zf.close()


def postprocess_all_html_pages(shared_resources, blog_root):
    for path, page in shared_resources.all_pages.items():
        page.transform()

    AddSidebar.add_to_all_relevant_pages()

    for path, page in shared_resources.all_pages.items():
        page.save(blog_root)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "EXPORT_ZIPFILE",
        help="Path to the export zipfile."
    )

    args = parser.parse_args()

    generate_blog(args.EXPORT_ZIPFILE, "blog")
