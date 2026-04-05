import os
import time
import shutil
from typing import Optional

from notion_blog_generator.virtual_fs import VirtualFS

from notion_blog_generator.settings import settings
from notion_blog_generator.thumb_cache import StoredThumbCache
from notion_blog_generator.preprocessors import get_preprocessors
from notion_blog_generator.postprocessors import get_postprocessors
from notion_blog_generator.html_transformers import get_transformers
from notion_blog_generator.html_transformers.generate_thumbnails import GenerateThumbnails


class BlogGenerator:
    _blog_tree: Optional[VirtualFS]

    def __init__(self, zipfile, blog_root):
        self._zipfile = zipfile
        self._blog_root = blog_root

        self._blog_tree = None

    @property
    def _root_node(self):
        return self._blog_tree.root

    def generate_blog(self):
        start_ts = time.time()

        thumb_cache = None
        if settings.generate_thumbnails:
            thumb_cache = StoredThumbCache.create_thumb_cache(self._blog_root)
            GenerateThumbnails.thumb_cache = thumb_cache

        _make_directory_empty(self._blog_root)

        self._blog_tree = VirtualFS(self._zipfile)

        self._run_preprocessors()
        self._run_html_transformers()
        self._run_postprocessors()

        self._blog_tree.store_on_disc(self._blog_root)

        if thumb_cache:
            thumb_cache.save_to_storage()

        settings.logger.info("Blog generated in %.2f seconds.",
                             time.time() - start_ts)

    def _run_preprocessors(self):
        for preprocessor in get_preprocessors():
            preprocessor.validate_requirements()
            preprocessor.preprocess(self._blog_tree, self._root_node)
            preprocessor.did_run = True

    def _run_html_transformers(self):
        for transformer in get_transformers():
            transformer.log_transformer()
            transformer.validate_requirements()

            for html_file in self._root_node.walk_htmls():
                transformer.transform(self._blog_tree, self._root_node, html_file)

            transformer.did_run = True

            if transformer.paralelized:
                transformer.finish_paralelization()

    def _run_postprocessors(self):
        for postprocessor in get_postprocessors():
            postprocessor.validate_requirements()
            postprocessor.postprocess(self._blog_tree, self._root_node)
            postprocessor.did_run = True


def _make_directory_empty(blog_path):
    blacklist = {
        ".git",
        ".gitignore",
        settings.thumb_cache_name,
    }
    if os.path.exists(blog_path) and "index.html" in os.listdir(blog_path):
        for item in os.listdir(blog_path):
            if item in blacklist:
                continue

            path = os.path.join(blog_path, item)

            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.unlink(path)

    os.makedirs(blog_path, exist_ok=True)
