"""
Sigh. Notion just out of random inserted some kind of hashes or UUID's into all
filenames, which of course fucks everything up beyond recognition.
"""
import re
import os.path
import zipfile
from typing import Union

import dhtmlparser

from lib import SharedResources
from lib.settings import settings


class VirtualFS:
    def __init__(self, shared_resources, zipfile):
        self.shared_resources = shared_resources

        self.lookup_table = self._build_lookup_table(shared_resources, zipfile)
        self.directory_map = self._build_directory_map(self.lookup_table)

        self._map_dirs_to_tree(self.directory_map)

        for filename, file in self.lookup_table.items():
            dirname = os.path.dirname(filename)
            directory = self.directory_map[dirname]
            directory.add_file(file)

        root_path = min(path for path in self.directory_map.keys())
        self.root = self.directory_map[root_path]

        resource_map = {}
        for html in self.root.walk_htmls():
            resource_map.update(html.refactor_resource_map(resource_map))

        print(resource_map)

    def _build_lookup_table(self, shared_resources, zipfile):
        lookup_table = {
            filename: data
            for filename, data in self._unpack_zipfile(zipfile)
        }
        return lookup_table

    def _unpack_zipfile(self, zipfile):
        settings.logger.info("Unpacking zipfile tree..")

        for zf, item in iterate_zipfile(zipfile):
            if item.filename.endswith(".html"):
                object = HtmlPage(zf.read(item).decode("utf-8"),
                                  self.shared_resources,
                                  original_fn=item.filename)
            else:
                object = Data(item.filename, zf.read(item))

            # settings.logger.debug("Unpacked `%s`", item.filename)
            yield item.filename, object

        settings.logger.info("Zipfile unpacked.")

    def _build_directory_map(self, lookup_table):
        directory_map = {
            os.path.dirname(path): Directory(os.path.basename(os.path.dirname(path)))
            for path in set(lookup_table.keys())
        }
        return directory_map

    def _map_dirs_to_tree(self, directory_map):
        for path, directory in directory_map.items():
            dirname = os.path.dirname(path)
            parent_dir = directory_map.get(dirname)

            if parent_dir and parent_dir != directory:
                directory.set_parent(parent_dir)
                parent_dir.add_subdir(directory)


class ResourceRegistry:
    def __init__(self):
        self._id_counter = 0

        self._path_to_item = {}
        self._path_to_id = {}
        self._id_to_item = {}
        self._id_to_path = {}

    def add_item(self, path, resource):
        id = self._path_to_id.get(path)
        if id:
            return id

        self._path_to_item[path] = resource

        id = self._inc_id()

        self._path_to_id[path] = id
        self._id_to_item[id] = resource
        self._id_to_path[id] = path

        return id

    def item_by_path(self, path):
        return self._path_to_item.get(path)

    def item_by_id(self, id):
        return self._id_to_item.get(id)

    def path_by_id(self, id):
        return self._id_to_path.get(id)

    def id_by_path(self, path):
        return self._path_to_id.get(path)

    def _inc_id(self):
        id = self._id_counter
        self._id_counter += 1
        return id


class FileBase:
    def __init__(self):
        self.parent = None

    @property
    def filename(self):
        return "FileBase"

    def set_parent(self, parent):
        self.parent = parent

    @property
    def path(self):
        path = [self.filename]
        parent = self.parent
        while parent:
            path.append(parent.filename)
            parent = parent.parent

        path.reverse()

        if len(path) > 1:
            return os.path.join(*path)

        return path[0]


class HtmlPage(FileBase):
    DEFAULT_WIDTH = 900  # 900 is the max width on the page

    def __init__(self, content, shared: SharedResources, original_fn=None):
        super().__init__()

        self.content = content
        self.shared = shared
        self.dom = dhtmlparser.parseString(self.content)

        self.original_fn = original_fn  # TODO: can be used to generate trans table

        self.is_index = False

    @property
    def filename(self):
        return self.original_fn

    @property
    def debug_fn(self):
        return os.path.basename(self.original_fn)

    @property
    def title(self):
        return self.dom.find("h1", {"class": "page-title"})[0].getContent()

    def refactor_resource_map(self, resource_map):
        links = (a for a in self.dom.find("a")
                 if "://" not in a.params.get("href", ""))

        images = (img for img in self.dom.find("img")
                  if "://" not in img.params.get("src", ""))

        meta_links = (link for link in self.dom.find("link")
                      if "href" in link.params and \
                         "://" not in link.params.get("href", ""))

        resources = (
            (links, "href"),
            (images, "src"),
            (meta_links, "href"),
        )

        for resource_generator, src in resources:
            for resource in resource_generator:
                path = resource.params[src]
                abs_path = os.path.abspath(path)


class Data(FileBase):
    def __init__(self, original_path, content):
        super().__init__()

        self.original_path = original_path
        self.content = content

    @property
    def debug_fn(self):
        return os.path.basename(self.original_path)


class Directory(FileBase):
    def __init__(self, name):
        super().__init__()

        self.name = name

        self.subdirs = []
        self.files = []

    @property
    def filename(self):
        return self.name

    def __repr__(self):
        return "Directory(%s)" % self.name

    def add_subdir(self, subdir):
        self.subdirs.append(subdir)

    def add_file(self, file: Union[HtmlPage, Data]):
        self.files.append(file)
        file.set_parent(self)

    def print_tree(self, indent=0):
        print(indent * "  ", self.name + "/")

        for file in self.files:
            print((indent + 1) * "  ", file.debug_fn)

        for directory in self.subdirs:
            directory.print_tree(indent + 1)

    def walk_dirs(self):
        yield self

        for dir in self.subdirs:
            yield from dir.walk_dirs()

    def walk_files(self):
        for file in self.files:
            yield file

        for dir in self.subdirs:
            yield from dir.walk_files()

    def walk_htmls(self):
        for file in self.files:
            if isinstance(file, HtmlPage):
                yield file

        for dir in self.subdirs:
            yield from dir.walk_htmls()


def create_abstract_tree(shared_resources, zipfile):
    return VirtualFS(shared_resources, zipfile)



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
