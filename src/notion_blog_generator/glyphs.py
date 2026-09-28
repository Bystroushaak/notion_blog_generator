"""
Journey-style glyphs derived from Notion page UUIDs.

A glyph is a 7x7 bitmap made of four 3x3 parts separated by a one-cell gap.
The part alphabet is the one used by the game Journey: 15 base shapes, which
under rotation and mirroring give 61 distinct parts.
"""
from __future__ import annotations

import uuid
import random
from functools import lru_cache
from urllib.parse import quote

BASE_SHAPES = (
    "..# ... ###",
    "..# ..# ###",
    "..# .## ###",
    "..# #.. ##.",
    "..# #.# ..#",
    "..# #.# ###",
    "..# ### ..#",
    "..# ### #..",
    "#.# ... #.#",
    "#.# ... ###",
    "#.# ..# ###",
    "#.# .## ###",
    "#.# #.# #.#",
    "#.# #.# ###",
    "#.# ### #.#",
)
QUADRANT_OFFSETS = ((0, 0), (4, 0), (0, 4), (4, 4))
UUID_DIGITS = 22
LANGUAGE_PARTS = {
    "en": ((1, 0, 1), (0, 0, 0), (1, 0, 1)),
    "cz": ((1, 0, 1), (1, 0, 1), (1, 0, 1)),
}

INK = "#2e1f1c"
RUST = "#963f1e"

# cloth dyes: (light, mid, dark) gradient stops of the cloth, then the edge
# line and glyph ink. rust = articles, gold = categories, green = tags; blue is
# the manuscript alternative for categories
# free 7x7 drawings on the same cloth, for special pages where a recognizable
# picture beats an abstract name glyph
PICTOGRAMS = {
    "changelog": "#.##### ....... #.##### ....... #.####. ....... #.###..",
    "letter": "####### ##...## #.#.#.# #..#..# #.....# #.....# #######",
    "bookmark": ".#####. .#####. .#####. .#####. .##.##. .#...#. .......",
    "book": "....... ##...## #.#.#.# #..#..# #..#..# ##.#.## ..###..",
}

DYES = {
    "rust": ("#a64a26", "#963f1e", "#8d391b", "#fffaf2", "#fff1e0"),
    "blue": ("#1f8dbb", "#177aa6", "#12648a", "#fffaf2", "#fff1e0"),
    "green": ("#67995f", "#578a50", "#487643", "#fffaf2", "#fff1e0"),
    "gold": ("#fbf3e2", "#f4e8cc", "#eadbb8", "#c89a3a", "#b8862b"),
}


def is_page_uuid(value: str) -> bool:
    """Generated pages (tags, ..) carry a filename instead of a Notion UUID."""
    try:
        uuid.UUID(value)
    except ValueError:
        return False

    return True


def name_glyph(page_uuid: str) -> Glyph:
    """
    Mirror-symmetric glyph, like Journey's "primary alphabet" used for names.

    One bit picks the mirror axis, two base-61 digits pick the free quadrants,
    so there are 7,381 distinct name glyphs. Short fingerprint, not unique.
    """
    number = uuid.UUID(page_uuid).int
    number, vertical_axis = divmod(number, 2)
    number, first = divmod(number, len(PARTS))
    number, second = divmod(number, len(PARTS))
    a, b = PARTS[first], PARTS[second]

    if vertical_axis:
        return a, flip_horizontally(a), b, flip_horizontally(b)

    return a, b, flip_vertically(a), flip_vertically(b)


def uuid_as_glyphs(page_uuid: str, language: str) -> list[Glyph]:
    """
    Write the full 128-bit UUID as base-61 digits, four digits per glyph.

    61**22 > 2**128, so 22 quadrants carry the UUID losslessly. The last two
    quadrants of the sixth glyph would always be zero; they carry the language.
    """
    number = uuid.UUID(page_uuid).int
    quadrants = []
    for _ in range(UUID_DIGITS):
        number, digit = divmod(number, len(PARTS))
        quadrants.append(PARTS[digit])

    quadrants += [LANGUAGE_PARTS[language]] * 2

    return [tuple(quadrants[i : i + 4]) for i in range(0, len(quadrants), 4)]


def glyphs_to_uuid(glyphs: list[Glyph]) -> tuple[str, str]:
    """Inverse of `uuid_as_glyphs()`: return the UUID and the language."""
    quadrants = [part for glyph in glyphs for part in glyph]
    number = sum(
        PARTS.index(part) * len(PARTS) ** i for i, part in enumerate(quadrants[:UUID_DIGITS])
    )
    language = next(lang for lang, part in LANGUAGE_PARTS.items() if part == quadrants[-1])

    return str(uuid.UUID(int=number)), language


def render_svg(glyph: Glyph, ink: str) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 7 7" fill="{ink}" '
        f'shape-rendering="crispEdges">{glyph_rects(glyph, 0, 0, 1)}</svg>'
    )


def render_strip(
    page_uuid: str, language: str, dye: str = "rust", pictogram: str | None = None
) -> str:
    """
    Journey-style cloth strip: frayed ends, rusty cloth, glowing double edge
    lines, the name glyph (or a pictogram) on top and the whole UUID plus
    language written below as six small glyphs.
    """
    width, height = 15, 29
    key = page_uuid[:8]
    light, mid, dark, line, ink = DYES[dye]
    outline = frayed_outline(page_uuid, width, height, 1.3)
    edge_lines = edge_line_rects(width, height, ((0.7, 0.3), (1.4, 0.2)))

    small_glyphs = []
    for index, glyph in enumerate(uuid_as_glyphs(page_uuid, language)):
        row, column = divmod(index, 2)
        small_glyphs.append(glyph_rects(glyph, 2.8 + column * 5.9, 13 + row * 4.8, 0.5))

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="-3 -3 {width + 6} {height + 6}">
  <defs>
    <clipPath id="cloth-{key}"><polygon points="{outline}"/></clipPath>
    <linearGradient id="dye-{key}" x1="0" y1="0" x2="0.3" y2="1">
      <stop offset="0" stop-color="{light}"/>
      <stop offset="0.6" stop-color="{mid}"/>
      <stop offset="1" stop-color="{dark}"/>
    </linearGradient>
    <pattern id="weave-{key}" width="0.5" height="0.5" patternUnits="userSpaceOnUse">
      <rect width="0.5" height="0.07" fill="#f6e3cc" opacity="0.07"/>
      <rect width="0.07" height="0.5" fill="#3a1408" opacity="0.08"/>
    </pattern>
    <filter id="bloom-{key}" x="-40%" y="-15%" width="180%" height="130%">
      <feGaussianBlur stdDeviation="0.35" result="near"/>
      <feGaussianBlur in="SourceGraphic" stdDeviation="1.3" result="far"/>
      <feMerge><feMergeNode in="far"/><feMergeNode in="far"/><feMergeNode in="near"/></feMerge>
    </filter>
    <filter id="soft-bloom-{key}" x="-10%" y="-10%" width="120%" height="120%">
      <feGaussianBlur stdDeviation="0.3"/>
    </filter>
    <g id="edges-{key}" clip-path="url(#cloth-{key})" fill="{line}">{edge_lines}</g>
    <g id="glyphs-{key}" clip-path="url(#cloth-{key})" fill="{ink}" shape-rendering="crispEdges">
      {mark_rects(page_uuid, pictogram, 4, 3.2)}
      {"".join(small_glyphs)}
    </g>
  </defs>
  <g clip-path="url(#cloth-{key})">
    <rect width="{width}" height="{height}" fill="url(#dye-{key})"/>
    <rect width="{width}" height="{height}" fill="url(#weave-{key})"/>
  </g>
  <use href="#edges-{key}" filter="url(#bloom-{key})" opacity="0.9"/>
  <use href="#glyphs-{key}" filter="url(#soft-bloom-{key})" opacity="0.6"/>
  <use href="#edges-{key}"/>
  <use href="#glyphs-{key}"/>
</svg>"""


@lru_cache(maxsize=None)
def tag_data_uri(page_uuid: str, dye: str = "rust", pictogram: str | None = None) -> str:
    """
    Short cloth tag with just the name glyph, for inline use next to links.

    Returned as a data URI for an <img>: the page then gets one element per
    link instead of a parsed SVG subtree, and ids inside the standalone SVG
    document can't collide with the same tag elsewhere on the page.
    """
    return "data:image/svg+xml," + quote(render_tag(page_uuid, dye, pictogram))


def render_tag(page_uuid: str, dye: str = "rust", pictogram: str | None = None) -> str:
    width, height = 11, 12
    key = "tag"
    light, _, dark, line, ink = DYES[dye]
    outline = frayed_outline(page_uuid, width, height, 0.8)
    edge_lines = edge_line_rects(width, height, ((0.45, 0.35), (1.1, 0.2)))

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 -0.2 {width} {height + 0.4}">
  <defs>
    <clipPath id="cloth-{key}"><polygon points="{outline}"/></clipPath>
    <linearGradient id="dye-{key}" x1="0" y1="0" x2="0.3" y2="1">
      <stop offset="0" stop-color="{light}"/>
      <stop offset="1" stop-color="{dark}"/>
    </linearGradient>
  </defs>
  <g clip-path="url(#cloth-{key})">
    <rect width="{width}" height="{height}" fill="url(#dye-{key})"/>
    <g fill="{line}">{edge_lines}</g>
    <g fill="{ink}" shape-rendering="crispEdges">{mark_rects(page_uuid, pictogram, 2, 2.5)}</g>
  </g>
</svg>"""


def render_mark_svg(page_uuid: str, pictogram: str | None, ink: str) -> str:
    """Standalone 7x7 mark (name glyph or pictogram), for favicons and end marks."""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 7 7" fill="{ink}" '
        f'shape-rendering="crispEdges">{mark_rects(page_uuid, pictogram, 0, 0)}</svg>'
    )


def mark_rects(page_uuid: str, pictogram: str | None, left: float, top: float) -> str:
    if pictogram:
        return bitmap_rects(parse_shape(PICTOGRAMS[pictogram]), left, top, 1)

    return glyph_rects(name_glyph(page_uuid), left, top, 1)


def bitmap_rects(bitmap: Bitmap, left: float, top: float, scale: float) -> str:
    return "".join(
        f'<rect x="{left + x * scale:g}" y="{top + y * scale:g}" '
        f'width="{scale:g}" height="{scale:g}"/>'
        for y, row in enumerate(bitmap)
        for x, cell in enumerate(row)
        if cell
    )


def glyph_rects(glyph: Glyph, left: float, top: float, scale: float) -> str:
    rects = []
    for (dx, dy), part in zip(QUADRANT_OFFSETS, glyph):
        for y, row in enumerate(part):
            for x, cell in enumerate(row):
                if cell:
                    rects.append(
                        f'<rect x="{left + (dx + x) * scale:g}" y="{top + (dy + y) * scale:g}" '
                        f'width="{scale:g}" height="{scale:g}"/>'
                    )

    return "".join(rects)


def frayed_outline(page_uuid: str, width: int, height: int, depth: float) -> str:
    """Polygon of a cloth piece with torn top and bottom ends, stable per UUID."""
    fray = random.Random(page_uuid)
    top_edge = [(x / 2, fray.uniform(0, depth)) for x in range(width * 2 + 1)]
    bottom_edge = [(x / 2, height - fray.uniform(0, depth)) for x in range(width * 2, -1, -1)]

    return " ".join(f"{x:g},{y:.2f}" for x, y in top_edge + bottom_edge)


def edge_line_rects(width: int, height: int, lines: tuple[tuple[float, float], ...]) -> str:
    """Double lines along both long edges; `lines` are (offset, thickness) from the left edge."""
    mirrored = [(width - offset - thickness, thickness) for offset, thickness in lines]
    return "".join(
        f'<rect x="{x:g}" y="0" width="{w:g}" height="{height}"/>' for x, w in (*lines, *mirrored)
    )


def flip_horizontally(part: Bitmap) -> Bitmap:
    return tuple(tuple(row[::-1]) for row in part)


def flip_vertically(part: Bitmap) -> Bitmap:
    return tuple(part[::-1])


def rotate(part: Bitmap) -> Bitmap:
    return tuple(tuple(part[2 - x][y] for x in range(3)) for y in range(3))


def parse_shape(shape: str) -> Bitmap:
    return tuple(tuple(1 if cell == "#" else 0 for cell in row) for row in shape.split())


def build_parts() -> list[Bitmap]:
    """
    All rotations and mirrors of the base shapes, sorted. The order is part of
    the encoding: changing it changes every published glyph.
    """
    parts = set()
    for shape in BASE_SHAPES:
        part = parse_shape(shape)
        for _ in range(4):
            parts.add(part)
            parts.add(flip_horizontally(part))
            part = rotate(part)

    return sorted(parts)


Bitmap = tuple[tuple[int, ...], ...]
Glyph = tuple[Bitmap, Bitmap, Bitmap, Bitmap]

PARTS = build_parts()
