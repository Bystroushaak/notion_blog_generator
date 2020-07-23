from typing import Union
from typing import Iterator

from lib.virtual_fs.data import Data
from lib.virtual_fs.html_page import HtmlPage
from lib.virtual_fs.file_baseclass import FileBase


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
        subdir.set_parent(self)

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

    def walk_dirs(self) -> Iterator["Directory"]:
        yield self

        for dir in self.subdirs:
            yield from dir.walk_dirs()

    def walk_files(self) -> Iterator[Union[HtmlPage, Data]]:
        for file in self.files:
            yield file

        for dir in self.subdirs:
            yield from dir.walk_files()

    def walk_htmls(self) -> Iterator[HtmlPage]:
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

    def subdir_by_name(self, name, case_insensitive=False, default=None):
        for directory in self.subdirs:
            if directory.filename == name:
                return directory

            if case_insensitive and directory.filename.lower() == name.lower():
                return directory

        if default:
            return default

        raise ValueError("Couldn't find subdirectory `%s`." % name)

    @property
    def root_section(self):
        if self.parent:
            return self.parent.root_section

        return self.subdir_by_name("en")


class RootSection(Directory):
    """
    RootSection is special kind of directory used for language mutations.
    """
    def __init__(self, filename):
        super().__init__(filename)

        self.tags = []
        self.changelog = None

    @classmethod
    def make_from(cls, dir):
        root_section = cls(dir.filename)

        root_section.files = dir.files
        root_section.subdirs = dir.subdirs

        root_section.inner_index = dir.inner_index
        root_section.inner_index.is_index_to = root_section
        root_section.outer_index = dir.outer_index
        root_section.outer_index.is_index_to = root_section

        root_section.parent = dir.parent
        root_section.reindex_parents()

        return root_section

    @property
    def title(self):
        return self.filename

    def __repr__(self):
        return "RootSection(%s)" % self.filename

    @property
    def root_section(self):
        return self
