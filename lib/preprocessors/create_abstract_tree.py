"""
Sigh. Notion just out of random inserted some kind of hashes or UUID's into all
filenames, which of course fucks everything up beyond recognition.
"""
import re
import os.path
import zipfile
from typing import Union

import dhtmlparser

from lib.settings import settings


class VirtualFS:
    def __init__(self, zipfile):
        self.lookup_table = self._build_lookup_table(zipfile)
        self.directory_map = self._build_directory_map(self.lookup_table)

        self._map_dirs_to_tree(self.directory_map)

        for filename, file in self.lookup_table.items():
            dirname = os.path.dirname(filename)
            directory = self.directory_map[dirname]
            directory.add_file(file)

        root_path = min(path for path in self.directory_map.keys())
        self.root = self.directory_map[root_path]

        self.resource_registry = ResourceRegistry(self.root)
        for html in self.root.walk_htmls():
            html.convert_resources_to_ids(self.resource_registry)

        print(self.resource_registry)

    def _build_lookup_table(self, zipfile):
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
                                  original_fn=item.filename)
            elif item.filename.endswith("/"):
                continue  # dirs are created later
            else:
                object = Data(item.filename, zf.read(item))

            # settings.logger.debug("Unpacked `%s`", item.filename)
            yield item.filename, object

        settings.logger.info("Zipfile unpacked.")

    def _build_directory_map(self, lookup_table):
        directory_map = {
            os.path.dirname(path): Directory(os.path.basename(os.path.dirname(path)))
            for path in lookup_table.keys()
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
    def __init__(self, root):
        self._id_counter = 0

        self._path_to_item = {}
        self._path_to_id = {}
        self._id_to_item = {}
        self._id_to_path = {}

        self._full_path_lookup_table = {item.path: item
                                        for item in root.walk_all()}

        for key in self._full_path_lookup_table.keys():
            self.add_item(key)

    def add_item(self, path):
        id = self._path_to_id.get(path)
        if id:
            return id

        resource = self._full_path_lookup_table[path]

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
            full_path = os.path.join(*path)
        else:
            full_path = path[0]

        if not full_path.startswith("/"):
            full_path = "/" + full_path

        return full_path


class HtmlPage(FileBase):
    DEFAULT_WIDTH = 900  # 900 is the max width on the page

    def __init__(self, content, original_fn=None):
        super().__init__()

        self.content = content
        self.dom = dhtmlparser.parseString(self.content)

        # TODO: can be used to generate trans table
        self.original_fn = os.path.basename(original_fn)

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

    def convert_resources_to_ids(self, resource_registry: ResourceRegistry):
        resources = self._collect_resources()

        for resource_generator, src in resources:
            for resource_el in resource_generator:
                resource_path = resource_el.params[src]
                dirname = os.path.dirname(self.path)
                full_resource_path = os.path.join(dirname, resource_path)
                abs_path = os.path.abspath(full_resource_path)

                resource_id = resource_registry.add_item(abs_path)
                resource_el.params[src] = "resource:%d" % resource_id

    def convert_resources_to_paths(self, resource_registry: ResourceRegistry):
        resources = self._collect_resources()

        html_dir = os.path.dirname(self.path)

        for resource_generator, src in resources:
            for resource_el in resource_generator:
                resource_id_token = resource_el.params[src]
                if not resource_id_token.startswith("resource"):
                    continue

                resource_id = int(resource_id_token.split(":")[-1])
                resource = resource_registry.item_by_id(resource_id)
                resource_relpath = os.path.relpath(resource.path, html_dir)

                resource_el.params[src] = resource_relpath

    def _collect_resources(self):
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

        return resources


class Data(FileBase):
    def __init__(self, original_path, content):
        super().__init__()

        self._filename = os.path.basename(original_path)
        self.original_path = original_path
        self.content = content

    @property
    def filename(self):
        return self._filename

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

    def walk_all(self):
        yield self

        for file in self.files:
            yield file

        for dir in self.subdirs:
            yield from dir.walk_all()

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
