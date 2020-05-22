from .squash_toplevel_directory import SquashToplevelDirectory
from .generate_indexes_for_directories import GenerateIndexesForDirectories
from .unfuck_filenames import UnfuckFilenames


def get_preprocessors():
    return (
        SquashToplevelDirectory,
        GenerateIndexesForDirectories,
        UnfuckFilenames,
    )
