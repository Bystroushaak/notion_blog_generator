"""
Sigh. Notion just out of random inserted some kind of hashes or UUID's into all
filenames, which of course fucks everything up beyond recognition.
"""
import re
import os.path
import zipfile

import dhtmlparser

from lib import SharedResources
from lib.settings import settings


class HtmlPage:
    DEFAULT_WIDTH = 900  # 900 is the max width on the page

    def __init__(self, content, shared: SharedResources, original_fn=None):
        self.content = content
        self.shared = shared
        self.dom = dhtmlparser.parseString(self.content)

        self.original_fn = original_fn  # TODO: can be used to generate trans table

        self.is_index = False

    @property
    def title(self):
        return self.dom.find("h1", {"class": "page-title"})[0].getContent()


class Data:
    def __init__(self, filename, content):
        self.filename = filename
        self.content = content


class Directory:
    def __init__(self, name):
        self.name = name
        self.parent = None

        self.subdirs = []
        self.items = []

    def __repr__(self):
        return "Directory(%s)" % self.name

    def print_tree(self, indent=0):
        print(indent * "  ", self.name + "/")

        for directory in self.subdirs:
            directory.print_tree(indent + 1)


def create_abstract_tree(shared_resources, zipfile):
    lookup_table = {
        filename: data
        for filename, data in unpack_zipfile(shared_resources, zipfile)
    }

    directory_map = {
        os.path.dirname(path): Directory(os.path.basename(os.path.dirname(path)))
        for path in set(lookup_table.keys())
    }

    _map_dirs_to_tree(directory_map)

    for filename, item in lookup_table.items():
        dirname = os.path.dirname(filename)
        directory = directory_map[dirname]
        directory.items.append(item)

    root_path = min(path for path in directory_map.keys())
    root = directory_map[root_path]

    return root


def _map_dirs_to_tree(directory_map):
    for path, directory in directory_map.items():
        dirname = os.path.dirname(path)
        parent_dir = directory_map.get(dirname)

        if parent_dir and parent_dir != directory:
            directory.parent = parent_dir
            parent_dir.subdirs.append(directory)


def unpack_zipfile(shared_resources, zipfile):
    settings.logger.info("Unpacking zipfile tree..")

    for zf, item in iterate_zipfile(zipfile):
        if item.filename.endswith(".html"):
            object = HtmlPage(zf.read(item).decode("utf-8"),
                              shared_resources,
                              original_fn=item.filename)
        else:
            object = Data(item.filename, zf.read(item))

        # settings.logger.debug("Unpacked `%s`", item.filename)
        yield item.filename, object

    settings.logger.info("Zipfile unpacked.")

    # for filename, data in create_abstract_tree(zipfile):
    #     if filename.endswith(".html"):
    #         page = Page(filename, data, shared_resources)
    #         shared_resources.add_page(filename, page)
    #         settings.logger.info("`%s` extracted and stored for postprocessing",
    #                              filename)
    #     else:
    #         _save_unpacked_data(blog_root, filename, data)
    #         settings.logger.info("`%s` extracted", filename)


def iterate_zipfile(zipfile_path):
    zf = zipfile.ZipFile(zipfile_path)

    for zip_info in zf.infolist():
        yield zf, zip_info

    zf.close()


def _patch_links(data):
    dom = dhtmlparser.parseString(data)

    for a in dom.find("a"):
        if "href" not in a.params or "://" in a.params.get("href", ""):
            continue

        a.params["href"] = _patch_filename(a.params["href"])

    for img in dom.find("img"):
        if "src" not in img.params or "://" in img.params.get("src", ""):
            continue

        img.params["src"] = _patch_filename(img.params["src"])

    return dom.__str__()


def _patch_filename(filename):
    # "English section 8f6665fa0621410daa32502748e3cc5d.html"
    # -> "English section"
    return re.sub(' [a-z0-9]{32}|%20[a-z0-9]{32}', '', filename)


def _patch_html_filename(original_fn, data):
    dom = dhtmlparser.parseString(data)

    h1 = dom.find("h1")

    if not h1:
        return _patch_filename(original_fn)

    return os.path.join(os.path.dirname(original_fn),
                        _normalize_unicode(h1[0].getContent()) + ".html")


def _normalize_unicode(unicode_name):
    ascii_name = unicode_name.replace(" ", "_")

    return ascii_name
