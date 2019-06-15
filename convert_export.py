#! /usr/bin/env python3
import os
import shutil
import os.path
import zipfile
import argparse


class SharedResources:
    pass


class Page:
    def __init__(self, path, content, shared):
        self.path = path
        self.content = content
        self.shared = shared

    def save(self, blog_path):
        path = os.path.join(blog_path, self.path)

        dirname = os.path.dirname(path)
        if not os.path.exists(dirname):
            os.makedirs(dirname, exist_ok=True)

        with open(path, "w") as f:
            f.write(self.content)

    def postprocess(self, all_pages):
        pass


def generate_blog(zipfile, blog_path):
    remove_old_blog(blog_path)

    shared_resources = SharedResources()

    all_pages = {}
    for zf, item in iterate_zipfile(zipfile):
        if item.filename.endswith(".html"):
            all_pages[item.filename] = Page(item.filename,
                                            zf.read(item).decode("utf-8"),
                                            shared_resources)
            print(item.filename, "extracted and stored for postprocessing")
        else:
            zf.extract(item, path=blog_path)
            print(item.filename, "extracted")

    postprocess_html(shared_resources, all_pages, blog_path)


def remove_old_blog(blog_path):
    if os.path.exists(blog_path):
        shutil.rmtree(blog_path)

    os.makedirs(blog_path, exist_ok=True)


def iterate_zipfile(zipfile_path):
    zf = zipfile.ZipFile(zipfile_path)

    for zip_info in zf.infolist():
        yield zf, zip_info

    zf.close()


def postprocess_html(shared_resources, all_pages, blog_path):
    find_and_rename_index_page(all_pages)

    for path, page in all_pages.items():
        page.postprocess(all_pages)
        page.save(blog_path)


def find_and_rename_index_page(all_pages):
    root_pages = [root_page for root_page in all_pages.values()
                  if not os.path.dirname(root_page.path)]

    if len(root_pages) != 1:
        raise ValueError("Fuck, multiple root pages, implement --root-page switch later.")

    root_page = root_pages[0]

    index_name = "index.html"
    all_pages[index_name] = root_page
    del all_pages[root_page.path]
    root_page.path = index_name


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "EXPORT_ZIPFILE",
        help="Path to the export zipfile."
    )

    args = parser.parse_args()

    generate_blog(args.EXPORT_ZIPFILE, "blog")
