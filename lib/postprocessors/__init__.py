from .add_changelog_to_index import AddMinichangelogToIndex
from .generate_atom_feed_from_changelog import GenerateAtomFeedFromChangelog
from .convert_twitter_card_to_abs_url import ConvertTwitterCardsToAbsURL
from .add_robots_and_sitemap import AddRobotsAndSitemap


def get_postprocessors():
    return (
        AddMinichangelogToIndex,
        GenerateAtomFeedFromChangelog,
        ConvertTwitterCardsToAbsURL,
        AddRobotsAndSitemap,
    )
