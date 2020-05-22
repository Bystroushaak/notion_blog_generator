from lib.preprocessors import UnfuckFilenames


def test_remove_html_entities():
    assert UnfuckFilenames._remove_html_entities("asd") == "asd"
    assert UnfuckFilenames._remove_html_entities("a &nbsp; b") == "a  b"
    assert UnfuckFilenames._remove_html_entities("a&x1293278;b") == "ab"
    assert UnfuckFilenames._remove_html_entities("a & b") == "a & b"
    assert UnfuckFilenames._remove_html_entities("a&b") == "a&b"
    assert UnfuckFilenames._remove_html_entities("a&b;") == "a"
