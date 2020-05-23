from lib.html_transformers.replace_inlined_style import ReplaceInlinedStyles
from lib.html_transformers.add_atom_feed import AddAtomFeed
from lib.html_transformers.add_file_icons import AddFileIcons


def get_transformers():
    return (
        ReplaceInlinedStyles,
        AddAtomFeed,
        AddFileIcons,
    )
