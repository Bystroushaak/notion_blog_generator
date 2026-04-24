import queue
import os.path
import zipfile
import tempfile
import threading

from tqdm import tqdm

from notion_blog_generator.settings import settings
from notion_blog_generator.virtual_fs.data import Data
from notion_blog_generator.virtual_fs.directory import Tags
from notion_blog_generator.virtual_fs.directory import Directory
from notion_blog_generator.virtual_fs.directory import RootSection
from notion_blog_generator.virtual_fs.sidebar import Sidebar
from notion_blog_generator.virtual_fs.html_page import HtmlPage
from notion_blog_generator.virtual_fs.resource_registry import ResourceRegistry


def _unwrap_nested_zip(zipfile_path):
    """
    If the ZIP contains a single .zip file, extract it to a temp file
    and return the path. Otherwise return the original path.
    """
    zf = zipfile.ZipFile(zipfile_path)
    entries = zf.infolist()

    if len(entries) == 1 and entries[0].filename.endswith(".zip"):
        settings.logger.info("Detected nested ZIP, extracting to temp file..")
        tmp = tempfile.NamedTemporaryFile(suffix=".zip", delete=False)
        with zf.open(entries[0]) as src:
            while chunk := src.read(1024 * 1024):
                tmp.write(chunk)
        tmp.close()
        zf.close()
        return tmp.name, True

    zf.close()
    return zipfile_path, False


def iterate_zipfile(zipfile_path):
    actual_path, is_temp = _unwrap_nested_zip(zipfile_path)

    try:
        zf = zipfile.ZipFile(actual_path)
        try:
            for zip_info in zf.infolist():
                yield zf, zip_info
        finally:
            zf.close()
    finally:
        if is_temp:
            os.unlink(actual_path)


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
            filename: data for filename, data in self._unpack_zipfile(zipfile)
        }

        # to avoid big git changelogs when the zip file is randomly ordered
        # so it tends to go into different branches when it feels like it
        sorted_lookup_table = {}
        for fn in sorted(lookup_table.keys()):
            sorted_lookup_table[fn] = lookup_table[fn]

        return sorted_lookup_table

    def _unpack_zipfile(self, zipfile):
        settings.logger.info("Unpacking zipfile tree..")

        for zf, item in iterate_zipfile(zipfile):
            if item.filename.endswith(".html"):
                object = HtmlPage(
                    zf.read(item).decode("utf-8"), original_fn=item.filename
                )
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

        full_path_lookup_table = {item.path: item for item in self.root.walk_all()}

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
        settings.logger.info("Converting resources to paths..")

        for html in self.root.walk_htmls():
            html.convert_resources_to_paths(self.resource_registry)

    def store_on_disc(self, blog_root_path):
        self.convert_resources_to_paths()

        settings.logger.info("Saving files to disc..")

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

        worker_queue = queue.Queue()
        all_files = list(self.root.walk_files())
        for file in all_files:
            file_path = file.path

            # because os.path.join() doesn't work with second argument starting
            # with /
            if file_path.startswith("/"):
                file_path = file_path[1:]

            full_file_path = os.path.join(blog_root_path, file_path)

            # file.save_as(full_file_path)
            worker_queue.put((file.save_as, full_file_path))

        threads = []
        progress_bar = tqdm(total=len(all_files))
        for _ in range(16):
            thread = threading.Thread(
                target=self._save_file_worker_thread, args=(worker_queue, progress_bar)
            )
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

    def _save_file_worker_thread(self, queue: queue.Queue, progress_bar):
        while not queue.empty():
            method, arg = queue.get()
            method(arg)
            progress_bar.update(1)
