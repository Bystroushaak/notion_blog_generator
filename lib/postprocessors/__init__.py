from lib.postprocessors.add_changelog_to_index import AddMinichangelogToIndex
from lib.postprocessors.generate_atom_feed_from_changelog import GenerateAtomFeedFromChangelog
from lib.postprocessors.convert_twitter_card_to_abs_url import ConvertTwitterCardsToAbsURL
from lib.postprocessors.add_robots_and_sitemap import AddRobotsAndSitemap
from lib.postprocessors.add_sidebars import AddSidebarsToAllPages
from lib.postprocessors.fix_interesting_articles import FixInterestingArticlesLinks
from lib.postprocessors.add_metadata_to_root import AddMetadataToRoot


def get_postprocessors():
    return (
        AddMetadataToRoot,
        FixInterestingArticlesLinks,
        AddMinichangelogToIndex,
        GenerateAtomFeedFromChangelog,
        ConvertTwitterCardsToAbsURL,
        AddRobotsAndSitemap,
        AddSidebarsToAllPages,
    )
