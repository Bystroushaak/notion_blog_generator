from lib.html_transformers.replace_inlined_styles import ReplaceInlinedStyles
from lib.html_transformers.add_atom_feed_tags import AddAtomFeedTags
from lib.html_transformers.add_file_icons import AddFileIcons
from lib.html_transformers.add_favicon_links import AddFaviconLinkTags
from lib.html_transformers.add_patreon_buttons import AddPatreonButtons
from lib.html_transformers.add_google_tags import AddGoogleTags
from lib.html_transformers.add_scripts_and_twitter_buttons import AddScriptsAndTwitterButtons
from lib.html_transformers.add_twitter_cards import AddTwitterCards
from lib.html_transformers.add_syntax_highlighting import AddSyntaxHighlighting
from lib.html_transformers.add_breadcrumbs import AddBreadcrumbs
from lib.html_transformers.fix_youtube_embeds import FixYoutubeEmbeds
from lib.html_transformers.fix_inlined_styles import FixInlinedStyles
from lib.html_transformers.fix_blockquotes import FixBlockquotes
from lib.html_transformers.fix_file_uploads import FixFileUploads
from lib.html_transformers.fix_checkboxes import FixCheckboxes
from lib.html_transformers.make_notion_links_local import MakeNotionLinksLocal
from lib.html_transformers.generate_thumbnails import GenerateThumbnails
from lib.html_transformers.add_meta_tags import AddMetaTags
from lib.html_transformers.unroll_categories import UnrollCategories
from lib.html_transformers.unroll_sections import UnrollSections
from lib.html_transformers.unroll_subpage_descriptions import UnrollSubpageDescriptions
from lib.html_transformers.sidebar_add_last_fivve_articles import SidebarAddLastFiveArticles
from lib.html_transformers.sidebar_add_backlinks import SidebarsAddBacklinks
from lib.html_transformers.process_images import ProcessImages
from lib.html_transformers.sidebar_add_blog_categories import SidebarAddBlogCategories


def get_transformers():
    return (
        ReplaceInlinedStyles,
        AddAtomFeedTags,
        AddFileIcons,
        AddFaviconLinkTags,
        AddPatreonButtons,
        AddSyntaxHighlighting,
        AddBreadcrumbs,
        FixYoutubeEmbeds,
        FixInlinedStyles,
        FixBlockquotes,
        FixFileUploads,
        FixCheckboxes,
        MakeNotionLinksLocal,
        GenerateThumbnails,
        AddTwitterCards,
        AddScriptsAndTwitterButtons,
        AddMetaTags,
        UnrollSections,
        UnrollSubpageDescriptions,
        UnrollCategories,
        SidebarAddLastFiveArticles,
        SidebarAddBlogCategories,
        SidebarsAddBacklinks,
        AddGoogleTags,
        ProcessImages,
    )
