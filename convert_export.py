#! /usr/bin/env python3
import os
import shutil
import os.path
import zipfile
import argparse

from lib import SharedResources
from lib.page import Page


def generate_blog(zipfile, blog_root):
    remove_old_blog(blog_root)

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

    shared_resources.generate_title_map()

    postprocess_all_html_pages(shared_resources, blog_root)
    shared_resources.save()

    shutil.copy(os.path.join(os.path.dirname(__file__), "favicon.ico"), blog_root)


def remove_old_blog(blog_path):
    if os.path.exists(blog_path):
        shutil.rmtree(blog_path)

    os.makedirs(blog_path, exist_ok=True)


def iterate_zipfile(zipfile_path):
    zf = zipfile.ZipFile(zipfile_path)

    for zip_info in zf.infolist():
        yield zf, zip_info

    zf.close()


def postprocess_all_html_pages(shared_resources, blog_path):
    for path, page in shared_resources.all_pages.items():
        page.postprocess()
        page.save(blog_path)

    find_and_rename_index_page(shared_resources, blog_path)


def find_and_rename_index_page(shared_resources, blog_path):
    root_pages = [root_page for root_page in shared_resources.all_pages.values()
                  if not os.path.dirname(root_page.path)]

    if len(root_pages) != 1:
        raise ValueError("Fuck, multiple root pages, implement --root-page switch later.")

    root_page = root_pages[0]

    os.rename(os.path.join(blog_path, root_page.path),
              os.path.join(blog_path, "index.html"))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "EXPORT_ZIPFILE",
        help="Path to the export zipfile."
    )

    args = parser.parse_args()

    generate_blog(args.EXPORT_ZIPFILE, "blog")
