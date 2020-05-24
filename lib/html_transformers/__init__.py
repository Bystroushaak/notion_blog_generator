from lib.html_transformers.replace_inlined_style import ReplaceInlinedStyles
from lib.html_transformers.add_atom_feed import AddAtomFeedTag
from lib.html_transformers.add_file_icons import AddFileIcons
from lib.html_transformers.add_favicon_link import AddFaviconLinkTag
from lib.html_transformers.add_patreon_button import AddPatreonButton
from lib.html_transformers.add_analytics_tag import AddAnalyticsTag
from lib.html_transformers.add_scripts_and_buttons import AddScriptsAndButtons
from lib.html_transformers.add_twitter_card import AddTwitterCard
from lib.html_transformers.add_syntax_highlighting import AddSyntaxHighlighting
from lib.html_transformers.add_breadcrumbs import AddBreadcrumbs
from lib.html_transformers.fix_youtube_embeds import FixYoutubeEmbeds


def get_transformers():
    return (
        ReplaceInlinedStyles,
        AddAtomFeedTag,
        AddFileIcons,
        AddFaviconLinkTag,
        AddPatreonButton,
        AddAnalyticsTag,
        AddScriptsAndButtons,
        AddTwitterCard,
        AddSyntaxHighlighting,
        AddBreadcrumbs,
        FixYoutubeEmbeds,
    )
