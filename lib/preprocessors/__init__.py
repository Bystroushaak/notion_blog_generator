from .squash_toplevel_directory import SquashToplevelDirectory
from .generate_indexes_for_directories import GenerateIndexesForDirectories
from .unfuck_filenames import UnfuckFilenames
from .convert_spaces_to_underscores import ConvertSpacesToUnderscores


def get_preprocessors():
    return (
        SquashToplevelDirectory,
        GenerateIndexesForDirectories,
        UnfuckFilenames,
        ConvertSpacesToUnderscores,
    )
