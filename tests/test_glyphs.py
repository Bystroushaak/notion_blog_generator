import uuid
from urllib.parse import unquote

from pytest import mark

from notion_blog_generator import glyphs

SELF_ARTICLE = "edb7f886-2aa3-4676-98a9-fcb9bd63c0b8"


def rotations_and_mirrors(part):
    variants = set()
    for _ in range(4):
        variants.add(part)
        variants.add(glyphs.flip_horizontally(part))
        part = glyphs.rotate(part)
    return variants


def test_alphabet_has_61_parts_in_15_classes():
    classes = {min(rotations_and_mirrors(part)) for part in glyphs.PARTS}
    assert len(glyphs.PARTS) == 61
    assert len(classes) == 15


def test_part_order_is_stable():
    # the order is part of the encoding; changing it changes every published glyph
    assert glyphs.PARTS[0] == ((0, 0, 1), (0, 0, 0), (1, 1, 1))
    assert glyphs.PARTS[-1] == ((1, 1, 1), (1, 1, 0), (1, 0, 1))


@mark.parametrize("language", ["en", "cz"])
def test_uuid_round_trip(language):
    for _ in range(200):
        page_uuid = str(uuid.uuid4())
        assert glyphs.glyphs_to_uuid(glyphs.uuid_as_glyphs(page_uuid, language)) == (
            page_uuid,
            language,
        )


def test_uuid_is_written_as_six_glyphs():
    assert len(glyphs.uuid_as_glyphs(SELF_ARTICLE, "en")) == 6


def test_name_glyph_is_mirror_symmetric():
    for _ in range(100):
        a, b, c, d = glyphs.name_glyph(str(uuid.uuid4()))
        horizontal = b == glyphs.flip_horizontally(a) and d == glyphs.flip_horizontally(c)
        vertical = c == glyphs.flip_vertically(a) and d == glyphs.flip_vertically(b)
        assert horizontal or vertical


def test_name_glyph_is_deterministic():
    assert glyphs.name_glyph(SELF_ARTICLE) == glyphs.name_glyph(SELF_ARTICLE)


def test_tag_data_uri_is_standalone_svg():
    uri = glyphs.tag_data_uri(SELF_ARTICLE)
    assert uri.startswith("data:image/svg+xml,")
    assert unquote(uri.split(",", 1)[1]) == glyphs.render_tag(SELF_ARTICLE)
    assert '"' not in uri


def test_strip_contains_all_glyph_cells():
    strip = glyphs.render_strip(SELF_ARTICLE, "en")
    name_cells = sum(
        cell for part in glyphs.name_glyph(SELF_ARTICLE) for row in part for cell in row
    )
    small_cells = sum(
        cell
        for glyph in glyphs.uuid_as_glyphs(SELF_ARTICLE, "en")
        for part in glyph
        for row in part
        for cell in row
    )
    edge_lines = 4
    assert strip.count("<rect x=") == name_cells + small_cells + edge_lines


@mark.parametrize(
    "value, expected",
    [
        (SELF_ARTICLE, True),
        (SELF_ARTICLE.replace("-", ""), True),
        ("python.html", False),
        ("Tags", False),
    ],
)
def test_is_page_uuid(value, expected):
    assert glyphs.is_page_uuid(value) is expected


def test_pictograms_are_7x7():
    for name, shape in glyphs.PICTOGRAMS.items():
        bitmap = glyphs.parse_shape(shape)
        assert len(bitmap) == 7 and all(len(row) == 7 for row in bitmap), name


def test_pictogram_replaces_name_glyph_in_tag():
    with_glyph = glyphs.render_tag(SELF_ARTICLE)
    with_picto = glyphs.render_tag(SELF_ARTICLE, "rust", "book")
    picto_rects = glyphs.bitmap_rects(glyphs.parse_shape(glyphs.PICTOGRAMS["book"]), 2, 2.5, 1)
    assert picto_rects in with_picto
    assert picto_rects not in with_glyph


def test_strip_with_pictogram_keeps_uuid_glyphs():
    strip = glyphs.render_strip(SELF_ARTICLE, "en", "rust", "changelog")
    small = glyphs.glyph_rects(glyphs.uuid_as_glyphs(SELF_ARTICLE, "en")[0], 2.8, 13, 0.5)
    assert small in strip
    assert (
        glyphs.bitmap_rects(glyphs.parse_shape(glyphs.PICTOGRAMS["changelog"]), 4, 3.2, 1) in strip
    )
