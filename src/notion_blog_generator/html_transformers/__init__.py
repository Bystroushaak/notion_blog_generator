from notion_blog_generator.html_transformers.replace_inlined_styles import ReplaceInlinedStyles
from notion_blog_generator.html_transformers.add_atom_feed_tags import AddAtomFeedTags
from notion_blog_generator.html_transformers.add_file_icons import AddFileIcons
from notion_blog_generator.html_transformers.add_favicon_links import AddFaviconLinkTags
from notion_blog_generator.html_transformers.add_patreon_buttons import AddPatreonButtons
from notion_blog_generator.html_transformers.add_google_tags import AddGoogleTags
from notion_blog_generator.html_transformers.add_scripts_and_twitter_buttons import AddScriptsAndTwitterButtons
from notion_blog_generator.html_transformers.add_social_cards import AddSocialCards
from notion_blog_generator.html_transformers.add_syntax_highlighting import AddSyntaxHighlighting
from notion_blog_generator.html_transformers.add_breadcrumbs import AddBreadcrumbs
from notion_blog_generator.html_transformers.fix_youtube_embeds import FixYoutubeEmbeds
from notion_blog_generator.html_transformers.fix_inlined_styles import FixInlinedStyles
from notion_blog_generator.html_transformers.fix_blockquotes import FixBlockquotes
from notion_blog_generator.html_transformers.fix_file_uploads import FixFileUploads
from notion_blog_generator.html_transformers.fix_checkboxes import FixCheckboxes
from notion_blog_generator.html_transformers.fix_code_blocks_dir import FixCodeBlocksDir
from notion_blog_generator.html_transformers.fix_toggle_blocks import FixToggleBlocks
from notion_blog_generator.html_transformers.make_notion_links_local import MakeNotionLinksLocal
from notion_blog_generator.html_transformers.generate_thumbnails import GenerateThumbnails
from notion_blog_generator.html_transformers.add_meta_tags import AddMetaTags
from notion_blog_generator.html_transformers.unroll_categories import UnrollCategories
from notion_blog_generator.html_transformers.unroll_sections import UnrollSections
from notion_blog_generator.html_transformers.unroll_subpage_descriptions import UnrollSubpageDescriptions
from notion_blog_generator.html_transformers.sidebar_add_last_five_articles import SidebarAddLastFiveArticles
from notion_blog_generator.html_transformers.sidebar_add_backlinks import SidebarsAddBacklinks
from notion_blog_generator.html_transformers.process_images import ProcessImages
from notion_blog_generator.html_transformers.sidebar_add_blog_categories import SidebarAddBlogCategories


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
        FixCodeBlocksDir,
        FixToggleBlocks,
        MakeNotionLinksLocal,
        AddSocialCards,
        GenerateThumbnails,
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
