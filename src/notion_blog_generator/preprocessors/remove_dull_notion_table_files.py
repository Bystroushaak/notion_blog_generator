from notion_blog_generator.settings import settings

from .preprocessor_base import PreprocessorBase

from notion_blog_generator.virtual_fs import Directory
from notion_blog_generator.virtual_fs import VirtualFS


class RemoveDullNotionTableFiles(PreprocessorBase):
    @classmethod
    def preprocess(cls, virtual_fs: VirtualFS, root: Directory):
        settings.logger.info("Removing dull notion.so table files..")

        for dir in root.walk_dirs():
            if dir.filename.startswith("Interesting_articles") and dir.parent is root:
                cls._empty_directory(dir)

        # collect first; removing while walk_htmls() iterates parent.files skips every other page
        empty_pages = [page for page in root.walk_htmls() if cls._has_empty_body(page)]
        for page in empty_pages:
            page.parent.files.remove(page)

        # a table directory left without rows would still make its page look like a category
        for directory in {page.parent for page in empty_pages}:
            cls._remove_if_empty(directory)

    @staticmethod
    def _has_empty_body(page) -> bool:
        page_body_tags = page.dom.find("div", {"class": "page-body"})
        return bool(page_body_tags) and not page_body_tags[0].content_str().strip()

    @classmethod
    def _empty_directory(cls, dir):
        dir.files = [file for file in dir.files
                     if file.filename == "index.html"]

    @classmethod
    def _remove_if_empty(cls, directory: Directory):
        if directory.files or directory.subdirs or directory.parent is None:
            return

        parent = directory.parent
        parent.subdirs.remove(directory)
        cls._remove_if_empty(parent)
