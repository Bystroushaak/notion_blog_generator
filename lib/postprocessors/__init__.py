from .make_changelog_readable import MakeChangelogReadable
from .add_changelog_to_index import AddMinichangelogToIndex
from .add_sidebars import AddSidebarsToAllPages
from .generate_atom_feed_from_changelog import GenerateAtomFeedFromChangelog


def get_postprocessors():
    return (
        MakeChangelogReadable,
        AddMinichangelogToIndex,
        AddSidebarsToAllPages,
        GenerateAtomFeedFromChangelog,
    )
