#! /usr/bin/env python3
import os
import sys
import shutil
import os.path
import zipfile
import argparse

import dhtmlparser


class SharedResources:
    def __init__(self, blog_root):
        self.css = ""
        self._css_path = "style.css"
        self._blog_root = blog_root

    def add_css(self, css):
        self.css = css

        return self._css_path

    def save(self):
        with open(os.path.join(self._blog_root, self._css_path), "w") as f:
            f.write(self.css.strip() + "\n\n")


class Page:
    def __init__(self, path: str, content, shared):
        self.path = path
        self.content = content
        self.shared = shared
        self.dom = dhtmlparser.parseString(self.content)

    def save(self, blog_path):
        path = os.path.join(blog_path, self.path)

        dirname = os.path.dirname(path)
        if not os.path.exists(dirname):
            os.makedirs(dirname, exist_ok=True)

        with open(path, "w") as f:
            f.write(self.dom.prettify())

    def postprocess(self, all_pages):
        self._remove_inlined_style(self.dom)
        self._add_utf_declaration(self.dom)
        self._add_atom_feed(self.dom)

    def _remove_inlined_style(self, dom):
        style = dom.match("head", "style")[0]

        style_path = self.shared.add_css(style.getContent())
        style_path = ("../" * self.path.count("/")) + style_path

        style_str = '<link rel="stylesheet" type="text/css" href="%s">' % style_path
        new_style = dhtmlparser.parseString(style_str).find("link")[0]

        style.replaceWith(new_style)

    def _add_utf_declaration(self, dom):
        head = dom.find("head")[0]

        utf_tag_str = '<meta http-equiv="Content-Type" content="text/html; charset=utf-8">'
        utf_tag = dhtmlparser.parseString(utf_tag_str).find("meta")[0]

        head.childs.append(utf_tag)

    def _add_atom_feed(self, dom):
        head = dom.find("head")[0]

        atom_tag_str = (
            '<link rel="alternate" type="application/atom+xml" '
            'href="http://rfox.eu/raw/feeds/notion_blog.xml" />'
        )
        atom_tag = dhtmlparser.parseString(atom_tag_str).find("link")[0]

        head.childs.append(atom_tag)


def generate_blog(zipfile, blog_path):
    remove_old_blog(blog_path)

    shared_resources = SharedResources(blog_path)

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
    shared_resources.save()


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
