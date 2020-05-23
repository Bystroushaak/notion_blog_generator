from lib.html_transformers.replace_inlined_style import ReplaceInlinedStyles
from lib.html_transformers.add_atom_feed import AddAtomFeed


def get_transformers():
    return (
        ReplaceInlinedStyles,
        AddAtomFeed,
    )
