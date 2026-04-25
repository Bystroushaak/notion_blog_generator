from notion_blog_generator.postprocessors.add_changelog_to_index import AddMinichangelogToIndex
from notion_blog_generator.postprocessors.generate_atom_feed_from_changelog import GenerateAtomFeedFromChangelog
from notion_blog_generator.postprocessors.convert_twitter_card_to_abs_url import ConvertTwitterCardsToAbsURL
from notion_blog_generator.postprocessors.add_robots_and_sitemap import AddRobotsAndSitemap
from notion_blog_generator.postprocessors.add_sidebars import AddSidebarsToAllPages
from notion_blog_generator.postprocessors.fix_interesting_articles import FixInterestingArticlesLinks
from notion_blog_generator.postprocessors.add_metadata_to_root import AddMetadataToRoot
from notion_blog_generator.postprocessors.move_cover_image_to_top import MoveCoverImageToTop


def get_postprocessors():
    return (
        FixInterestingArticlesLinks,
        AddMinichangelogToIndex,
        AddMetadataToRoot,
        GenerateAtomFeedFromChangelog,
        ConvertTwitterCardsToAbsURL,
        AddRobotsAndSitemap,
        AddSidebarsToAllPages,
        MoveCoverImageToTop,
    )
