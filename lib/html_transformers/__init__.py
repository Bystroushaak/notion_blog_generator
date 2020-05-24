from lib.html_transformers.replace_inlined_style import ReplaceInlinedStyles
from lib.html_transformers.add_atom_feed import AddAtomFeedTag
from lib.html_transformers.add_file_icons import AddFileIcons
from lib.html_transformers.add_favicon_link import AddFaviconLinkTag
from lib.html_transformers.add_patreon_button import AddPatreonButton
from lib.html_transformers.add_analytics_tag import AddAnalyticsTag


def get_transformers():
    return (
        ReplaceInlinedStyles,
        AddAtomFeedTag,
        AddFileIcons,
        AddFaviconLinkTag,
        AddPatreonButton,
        AddAnalyticsTag,
    )
