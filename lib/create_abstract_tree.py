"""
Sigh. Notion just out of random inserted some kind of hashes or UUID's into all
filenames, which of course fucks everything up beyond recognition.
"""
import os.path
import zipfile
from typing import Union

import dhtmlparser

from lib.settings import settings


def iterate_zipfile(zipfile_path):
    zf = zipfile.ZipFile(zipfile_path)

    for zip_info in zf.infolist():
        yield zf, zip_info

    zf.close()


class VirtualFS:
    def __init__(self, zipfile):
        settings.logger.info("Generating virtual filesystem..")

        lookup_table = self._build_lookup_table(zipfile)
        directory_map = self._build_directory_map(lookup_table)

        self._map_dirs_to_tree(directory_map)

        for filename, file in lookup_table.items():
            dirname = os.path.dirname(filename)
            directory = directory_map[dirname]
            directory.add_file(file)

        root_path = min(path for path in directory_map.keys())
        self.root = directory_map[root_path]

        self.resource_registry = self._build_resource_registry()

        settings.logger.info("Virtual filesystem is ready.")

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

    def _build_resource_registry(self):

        full_path_lookup_table = {item.path: item
                                  for item in self.root.walk_all()}

        # register all items to the registry
        path_id_map = {}
        resource_registry = ResourceRegistry()
        for path, item in full_path_lookup_table.items():
            try:
                item_id = resource_registry.register_item(item)
                path_id_map[path] = item_id
            except KeyError:
                pass

        for html in self.root.walk_htmls():
            html.convert_resources_to_ids(path_id_map)

        return resource_registry

    def convert_resources_to_paths(self):
        settings.logger.info("Converting resource to paths..")

        for html in self.root.walk_htmls():
            html.convert_resources_to_paths(self.resource_registry)

        settings.logger.info("Conversion of resources to paths done.")

    def store_on_disc(self, blog_root_path):
        self.convert_resources_to_paths()

        for directory in self.root.walk_dirs():
            directory_path = directory.path

            if directory_path == "/":
                continue

            # because os.path.join() doesn't work with second argument starting
            # with /
            if directory_path.startswith("/"):
                directory_path = directory_path[1:]

            full_directory_path = os.path.join(blog_root_path, directory_path)
            os.makedirs(full_directory_path, exist_ok=True)

        for file in self.root.walk_files():
            file_path = file.path

            # because os.path.join() doesn't work with second argument starting
            # with /
            if file_path.startswith("/"):
                file_path = file_path[1:]

            full_file_path = os.path.join(blog_root_path, file_path)

            file.save_as(full_file_path)

        settings.logger.info("Files stored on disc.")

    def resolve_by_path(self, path):
        pass


class ResourceRegistry:
    def __init__(self):
        self._id_counter = 0

        self._item_to_id = {}
        self._id_to_item = {}

    def register_item(self, item):
        item_id = self._item_to_id.get(item)
        if item_id:
            return item_id

        item_id = self._inc_id()

        self._item_to_id[item] = item_id
        self._id_to_item[item_id] = item

        return item_id

    def register_item_as_ref_str(self, item):
        id = self.register_item(item)
        return self.as_ref_str(id)

    def item_by_id(self, id):
        return self._id_to_item.get(id)

    def id_by_item(self, item):
        return self._item_to_id.get(item)

    def item_by_ref_str(self, ref_str):
        id = self.parse_ref_str(ref_str)
        return self.item_by_id(id)

    @staticmethod
    def as_ref_str(id):
        return "resource:%d" % id

    @staticmethod
    def is_ref_str(ref_str):
        return ref_str.startswith("resource:")

    @staticmethod
    def parse_ref_str(ref_str):
        return int(ref_str.split(":")[-1])

    def _inc_id(self):
        id = self._id_counter
        self._id_counter += 1
        return id


class FileBase:
    def __init__(self):
        self.parent = None
        self.filename = "FileBase"

    def set_parent(self, parent):
        self.parent = parent

    @property
    def is_data(self):
        return False

    @property
    def is_html(self):
        return False

    @property
    def is_directory(self):
        return False

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

    def save_as(self, file_path):
        raise NotImplementedError()


class HtmlPage(FileBase):
    DEFAULT_WIDTH = 900  # 900 is the max width on the page

    def __init__(self, content, original_fn=None):
        super().__init__()

        self.content = content
        self.dom = dhtmlparser.parseString(self.content)

        # TODO: can be used to generate trans table
        self.original_fn = os.path.basename(original_fn)
        self.filename = self.original_fn

        self.is_index_to = None

    @property
    def is_html(self):
        return True

    @property
    def is_index(self):
        return bool(self.is_index_to)

    @property
    def title(self):
        title_el = self.dom.find("h1", {"class": "page-title"})[0]
        return dhtmlparser.removeTags(title_el.__str__()).strip()

    def convert_resources_to_ids(self, path_id_map):
        resources = self._collect_resources()

        for resource_generator, src in resources:
            for resource_el in resource_generator:
                if not resource_el.isTag():
                    continue

                resource_path = resource_el.params[src]
                dirname = os.path.dirname(self.path)
                full_resource_path = os.path.join(dirname, resource_path)
                abs_path = os.path.abspath(full_resource_path)

                try:
                    id = path_id_map[abs_path]
                    resource_el.params[src] = ResourceRegistry.as_ref_str(id)
                except KeyError:
                    try:
                        id = path_id_map[abs_path.replace("%20", " ")]
                        resource_el.params[src] = ResourceRegistry.as_ref_str(id)
                    except KeyError:
                        settings.logger.error("Link not found, skipping: %s",
                                              abs_path)
                        continue

    def convert_resources_to_paths(self, resource_registry: ResourceRegistry):
        resources = self._collect_resources()

        html_dir = os.path.dirname(self.path)

        for resource_generator, src in resources:
            for resource_el in resource_generator:
                if not resource_el.isTag():
                    continue

                resource_id_token = resource_el.params[src]
                if not ResourceRegistry.is_ref_str(resource_id_token):
                    continue

                resource = resource_registry.item_by_ref_str(resource_id_token)
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
        scripts = (script for script in self.dom.find("script")
                   if "src" in script.params and \
                      "://" not in script.params.get("href", ""))
        twitter_images = (meta for meta in self.dom.find("meta",
                                                     {"name": "twitter:image"})
                          if "://" not in meta.params.get("content", ""))

        resources = (
            (links, "href"),
            (images, "src"),
            (meta_links, "href"),
            (scripts, "src"),
            (twitter_images, "content"),
        )

        return resources

    def save_as(self, file_path):
        with open(file_path, "wt") as f:
            f.write(self.dom.__str__())

    def create_copy(self):
        copy = HtmlPage(
            self.dom.__str__(),
            self.original_fn,
        )
        copy.filename = self.filename
        copy.is_index_to = self.is_index_to

        return copy


class Data(FileBase):
    def __init__(self, original_path, content):
        super().__init__()

        self.filename = os.path.basename(original_path)
        self.original_path = original_path
        self.content = content

    @property
    def is_data(self):
        return True

    def save_as(self, file_path):
        with open(file_path, "wb") as f:
            f.write(self.content)


class Directory(FileBase):
    def __init__(self, filename):
        super().__init__()

        self.filename = filename

        self.subdirs = []
        self.files = []

        self.inner_index = None
        self.outer_index = None

    @property
    def title(self):
        return "dirname:" + self.filename

    @property
    def is_directory(self):
        return True

    def __repr__(self):
        return "Directory(%s)" % self.filename

    def add_subdir(self, subdir):
        self.subdirs.append(subdir)

    def add_file(self, file: Union[HtmlPage, Data]):
        self.files.append(file)
        file.set_parent(self)

    def add_copy_as_index(self, html_file: HtmlPage):
        index = html_file.create_copy()
        index.filename = "index.html"

        self.files.append(index)
        index.parent = self

        # used later to do all kinds of postprocessing
        index.is_index_to = self
        html_file.is_index_to = self

        self.inner_index = index
        self.outer_index = html_file

    def print_tree(self, indent=0):
        print(indent * "  ", self.filename + "/")

        for file in self.files:
            print((indent + 1) * "  ", file.filename)

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

    def reindex_parents(self):
        for file in self.files:
            file.parent = self

        for dir in self.subdirs:
            dir.parent = self
