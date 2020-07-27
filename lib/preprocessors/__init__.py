from .squash_toplevel_directory import SquashToplevelDirectory
from .generate_indexes_for_directories import GenerateIndexesForDirectories
from .unfuck_filenames import UnfuckFilenames
from .convert_spaces_to_underscores import ConvertSpacesToUnderscores
from .make_root_sections import MakeRootSections
from .add_static_files import AddStaticFiles
from .load_metadata import LoadMetadata
from .generate_tag_structure import GenerateTagStructure
from .collect_refs_to_other_pages import CollectRefsToOtherPages
from .make_changelog_readable import LoadChangelogsAndMakeThemReadable
from .remove_dull_notion_table_files import RemoveDullNotionTableFiles


def get_preprocessors():
    return (
        SquashToplevelDirectory,
        LoadMetadata,
        CollectRefsToOtherPages,
        UnfuckFilenames,
        ConvertSpacesToUnderscores,
        GenerateIndexesForDirectories,
        MakeRootSections,
        GenerateTagStructure,
        AddStaticFiles,
        LoadChangelogsAndMakeThemReadable,
        RemoveDullNotionTableFiles,
    )
