import os.path
import unicodedata

from notion_blog_generator.settings import settings
from notion_blog_generator.virtual_fs import VirtualFS
from notion_blog_generator.virtual_fs import Directory

from .preprocessor_base import PreprocessorBase
from .convert_spaces_to_underscores import ConvertSpacesToUnderscores


def _strip_diacritics(text):
    """Remove diacritics from text for comparison purposes."""
    nfkd = unicodedata.normalize("NFKD", text)
    return "".join(c for c in nfkd if not unicodedata.combining(c))


class GenerateIndexesForDirectories(PreprocessorBase):
    requires = [ConvertSpacesToUnderscores]

    @classmethod
    def preprocess(cls, virtual_fs: VirtualFS, root: Directory):
        settings.logger.info("Generating indexes for directories..")

        for dir, file in cls.all_dirs_that_contain_html_with_same_name(root):
            dir.add_copy_as_index(file)

    @classmethod
    def all_dirs_that_contain_html_with_same_name(cls, root):
        for dir in root.walk_dirs():
            dirname = os.path.basename(dir.path).strip()

            if not dir.parent:
                continue

            yield from cls._files_with_dirname(dir, dirname)

    @classmethod
    def _files_with_dirname(cls, dir, dirname):
        for file in dir.parent.files:
            filename = os.path.basename(file.filename)

            if not filename.endswith(".html"):
                continue

            if "." in filename:
                filename = filename.rsplit(".", 1)[0].strip()

            if dirname == filename:
                yield dir, file
            elif _strip_diacritics(dirname) == _strip_diacritics(filename):
                yield dir, file
