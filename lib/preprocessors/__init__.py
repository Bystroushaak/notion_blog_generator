from .squash_toplevel_directory import SquashToplevelDirectory
from .generate_indexes_for_directories import GenerateIndexesForDirectories
from .unfuck_filenames import UnfuckFilenames
from .convert_spaces_to_underscores import ConvertSpacesToUnderscores
from .rename_root_sections import RenameRootSections
from .add_static_files import AddStaticFiles
from .load_metadata import LoadMetadata


def get_preprocessors():
    return (
        SquashToplevelDirectory,
        GenerateIndexesForDirectories,
        UnfuckFilenames,
        ConvertSpacesToUnderscores,
        RenameRootSections,
        AddStaticFiles,
        LoadMetadata,
    )
