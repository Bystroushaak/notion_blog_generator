from lib.settings import settings

from .preprocessor_base import PreprocessorBase

from lib.virtual_fs import Directory
from lib.virtual_fs import VirtualFS


class RemoveDullNotionTableFiles(PreprocessorBase):
    @classmethod
    def preprocess(cls, virtual_fs: VirtualFS, root: Directory):
        settings.logger.info("Removing dull notion.so table files..")

        for dir in root.walk_dirs():
            if dir.filename.startswith("Interesting_articles") and dir.parent is root:
                cls._empty_directory(dir)

        for page in root.walk_htmls():
            page_body_tags = page.dom.find("div", {"class": "page-body"})
            if page_body_tags and not page_body_tags[0].getContent().strip():
                page.parent.files.remove(page)

    @classmethod
    def _empty_directory(cls, dir):
        dir.files = [file for file in dir.files
                     if file.filename == "index.html"]
