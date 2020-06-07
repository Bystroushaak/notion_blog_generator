from .add_changelog_to_index import AddMinichangelogToIndex
from .generate_atom_feed_from_changelog import GenerateAtomFeedFromChangelog
from .convert_twitter_card_to_abs_url import ConvertTwitterCardsToAbsURL


def get_postprocessors():
    return (
        AddMinichangelogToIndex,
        GenerateAtomFeedFromChangelog,
        ConvertTwitterCardsToAbsURL,
    )
