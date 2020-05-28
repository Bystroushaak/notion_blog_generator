from lib.html_transformers.replace_inlined_styles import ReplaceInlinedStyles
from lib.html_transformers.add_atom_feed_tags import AddAtomFeedTags
from lib.html_transformers.add_file_icons import AddFileIcons
from lib.html_transformers.add_favicon_links import AddFaviconLinkTags
from lib.html_transformers.add_patreon_buttons import AddPatreonButtons
from lib.html_transformers.add_analytics_tags import AddAnalyticsTags
from lib.html_transformers.add_scripts_and_twitter_buttons import AddScriptsAndTwitterButtons
from lib.html_transformers.add_twitter_cards import AddTwitterCards
from lib.html_transformers.add_syntax_highlighting import AddSyntaxHighlighting
from lib.html_transformers.add_breadcrumbs import AddBreadcrumbs
from lib.html_transformers.fix_youtube_embeds import FixYoutubeEmbeds
from lib.html_transformers.fix_inlined_styles import FixInlinedStyles
from lib.html_transformers.fix_blockquotes import FixBlockquotes
from lib.html_transformers.make_notion_links_local import MakeNotionLinksLocal
from lib.html_transformers.generate_thumbnails import GenerateThumbnails
from lib.html_transformers.load_metadata import LoadMetadata
from lib.html_transformers.add_keywords import AddKeywordMetadataTags


def get_transformers():
    return (
        LoadMetadata,
        ReplaceInlinedStyles,
        AddAtomFeedTags,
        AddFileIcons,
        AddFaviconLinkTags,
        AddPatreonButtons,
        AddAnalyticsTags,
        AddSyntaxHighlighting,
        AddBreadcrumbs,
        FixYoutubeEmbeds,
        FixInlinedStyles,
        FixBlockquotes,
        MakeNotionLinksLocal,
        GenerateThumbnails,
        AddTwitterCards,
        AddScriptsAndTwitterButtons,
        AddKeywordMetadataTags,
    )
