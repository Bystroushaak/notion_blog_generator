from .squash_toplevel_directory import SquashToplevelDirectory
from .generate_indexes_for_directories import GenerateIndexesForDirectories


def get_preprocessors():
    return (
        SquashToplevelDirectory,
        GenerateIndexesForDirectories,
    )
