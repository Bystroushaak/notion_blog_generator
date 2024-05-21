from lib.preprocessors import UnfuckFilenames


def test_remove_html_entities():
    assert UnfuckFilenames._remove_html_entities("asd") == "asd"
    assert UnfuckFilenames._remove_html_entities("a &nbsp; b") == "a  b"
    assert UnfuckFilenames._remove_html_entities("a&x1293278;b") == "ab"
    assert UnfuckFilenames._remove_html_entities("a & b") == "a & b"
    assert UnfuckFilenames._remove_html_entities("a&b") == "a&b"
    assert UnfuckFilenames._remove_html_entities("a&b;") == "a"


def test_remove_dup_underscores():
    assert UnfuckFilenames._remove_dup_underscores("asd") == "asd"
    assert UnfuckFilenames._remove_dup_underscores("as_d") == "as_d"
    assert UnfuckFilenames._remove_dup_underscores("as__d") == "as_d"
    assert UnfuckFilenames._remove_dup_underscores("as___d") == "as_d"
    assert UnfuckFilenames._remove_dup_underscores("_as___d") == "as_d"
    assert UnfuckFilenames._remove_dup_underscores("__as___d") == "as_d"
    assert UnfuckFilenames._remove_dup_underscores("asd_") == "asd"
    assert UnfuckFilenames._remove_dup_underscores("asd__") == "asd"
