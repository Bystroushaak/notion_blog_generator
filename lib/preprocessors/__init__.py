from .squash_toplevel_directory import SquashToplevelDirectory
from .generate_indexes_for_directories import GenerateIndexesForDirectories
from .unfuck_filenames import UnfuckFilenames
from .convert_spaces_to_underscores import ConvertSpacesToUnderscores
from .rename_root_sections import RenameRootSections


def get_preprocessors():
    return (
        SquashToplevelDirectory,
        GenerateIndexesForDirectories,
        UnfuckFilenames,
        ConvertSpacesToUnderscores,
        RenameRootSections,
    )
