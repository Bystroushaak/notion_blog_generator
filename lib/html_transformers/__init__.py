from lib.html_transformers.replace_inlined_style import ReplaceInlinedStyles


def get_transformers():
    return (
        ReplaceInlinedStyles,
    )
