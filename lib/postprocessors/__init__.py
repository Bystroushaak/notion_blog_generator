from .make_changelog_readable import MakeChangelogReadable
from .add_changelog_to_index import AddMinichangelogToIndex


def get_postprocessors():
    return (
        MakeChangelogReadable,
        AddMinichangelogToIndex,
    )
