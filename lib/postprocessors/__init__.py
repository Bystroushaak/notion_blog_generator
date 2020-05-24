from .add_changelog_to_index import AddChangelogToIndex


def get_postprocessors():
    return (
        AddChangelogToIndex,
    )
