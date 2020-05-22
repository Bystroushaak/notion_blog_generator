import re
import os.path
import unicodedata
from functools import lru_cache

import dhtmlparser

from lib.settings import settings

from .preprocessor_base import PreprocessorBase


class UnfuckFilenames(PreprocessorBase):
    @classmethod
    def preprocess(cls, virtual_fs, root):
        settings.logger.info("Unfucking filenames..")

        for item in root.walk_htmls():
            title = item.title

            if "://" in title:
                continue

            new_filename = cls._normalize_fn(title)

            if len(new_filename) > 60:
                new_filename = new_filename[:60]

                if "_" in new_filename:
                    new_filename = new_filename.rsplit("_", 1)[0]

            new_filename = cls._make_sure_filename_is_unique(item, new_filename)

            section_dir = cls._dir_in_parent_with_same_name_as(item)
            if section_dir:
                section_dir.filename = new_filename

            item.filename = new_filename + ".html"

        for item in root.walk_dirs():
            new_filename = cls._patch_filename(item.filename)
            settings.logger.debug("Walking %s, new %s", item.filename, new_filename)
            settings.logger.debug("parent: %s", item.parent)

            item.filename = cls._make_sure_filename_is_unique(item, new_filename)

    @classmethod
    def _normalize_fn(cls, filename):
        filename_dom = dhtmlparser.parseString(filename)
        new_filename = dhtmlparser.removeTags(filename_dom).strip()

        new_filename = cls.normalize(filename)

        new_filename = new_filename.replace('"', '')
        new_filename = new_filename.replace("'", "")
        new_filename = cls._remove_html_entities(new_filename)

        translation = new_filename.maketrans(" /;:,?()$§",
                                             "_---_-____")

        new_filename = new_filename.translate(translation)

        return new_filename

    @staticmethod
    def _remove_html_entities(s):
        output = ""
        in_entity = False
        in_entity_buffer = ""
        for c in s:
            if not in_entity and c != "&":
                output += c
                continue

            if not in_entity and c == "&":
                in_entity = True
                in_entity_buffer += c
                continue

            if in_entity:
                in_entity_buffer += c

                if c == ";":
                    in_entity = False
                    in_entity_buffer = ""
                    continue

                if c == " " or c == "\n":
                    in_entity = False
                    output += in_entity_buffer
                    in_entity_buffer = ""

        if in_entity_buffer:
            output += in_entity_buffer

        return output

    @classmethod
    def _make_sure_filename_is_unique(cls, item, new_filename):
        if not item.parent:
            return new_filename

        counter = 1
        working_fn_copy = new_filename
        while cls._parent_already_has_item_named(item, working_fn_copy):
            working_fn_copy = new_filename + ("_%d" % counter)
            counter += 1

        return working_fn_copy

    @staticmethod
    def _parent_already_has_item_named(item, fn):
        if not item.parent:
            return False

        for subitem in item.parent.subdirs + item.parent.files:
            if subitem.filename == fn and item is not subitem:
                return True

        return False

    @staticmethod
    def _dir_in_parent_with_same_name_as(item):
        filename = item.filename.rsplit(".", 1)[0]  # remove .html

        for subdir in item.parent.subdirs:
            settings.logger.debug("subdir.filename == filename (%s == %s)", subdir.filename, filename)
            if subdir.filename == filename:
                return subdir

        return None

    @classmethod
    def _patch_filename(cls, filename):
        # "English section 8f6665fa0621410daa32502748e3cc5d.html"
        # -> "English section"
        return re.sub(' [a-z0-9]{32}|%20[a-z0-9]{32}', '', filename)

    @classmethod
    def _patch_html_filename(cls, original_fn, data):
        dom = dhtmlparser.parseString(data)

        h1 = dom.find("h1")

        if not h1:
            return cls._patch_filename(original_fn)

        return os.path.join(os.path.dirname(original_fn),
                            cls._normalize_unicode(h1[0].getContent()) + ".html")

    @classmethod
    def _normalize_unicode(cls, unicode_name):
        ascii_name = unicode_name.replace(" ", "_")

        return ascii_name

    TRANSLATION_TABLE = {}  #: Here you can put exceptions from normalization.

    _DASH_VARIANTS = "‒–—―-‐—"
    TRANSLATION_TABLE.update({udash: "-" for udash in _DASH_VARIANTS})

    @staticmethod
    @lru_cache(None)
    def _really_normalize_char(char):
        """
        Use NFKD normalization to `char`. Return ``?`` if character couldn't be
        normalized.

        Args:
            char (unicode): Unicode character which should be normalized.

        Returns:
            unicode: Normalized character.
        """
        new_char = unicodedata.normalize('NFKD', char)
        new_char = new_char.encode('ascii', errors='replace')
        new_char = new_char.decode("utf-8")

        # 'Ǎ' is normalized to 'A?' and I want only 'A'
        if len(new_char) == 2:
            return new_char[0]

        return new_char

    @classmethod
    @lru_cache(None)
    def _normalize_char(cls, char):
        """
        Use :attr:`.TRANSLATION_TABLE` to translate `char`, or
        :func:`_really_normalize_char` if `char` wasn't found in
        attr:`.TRANSLATION_TABLE`.

        Attr:
            char (unicode): Character which should be translated/normalized.

        Returns:
            unicode: Normalized character.
        """
        return cls.TRANSLATION_TABLE.get(char, cls._really_normalize_char(char))

    @staticmethod
    @lru_cache(None)
    def _is_same_char(char):
        """
        Try to convert `char` to ``latin2`` encoding and compare them.

        Args:
            char (unicode): Character to test.

        Returns:
            bool: True if `char` is convertible to ``latin2`` and back.
        """
        try:
            translated = char.encode("latin2")
        except UnicodeEncodeError:
            return False

        return translated == char

    @classmethod
    def normalize(cls, inp):
        """
        Normalize `inp`. Leave only ``latin2`` acceptible characters, normalize
        everything else, using unicode `NFKD` normalization, or
        :attr:`TRANSLATION_TABLE`.

        Convert characters which couldn't be normalized to ``?``.

        Args:
            inp (unicode): Unicode string which should be normalized.

        Returns:
            unicode: Normalized string.
        """
        out = ""
        for char in inp:
            if not cls._is_same_char(char):
                char = cls._normalize_char(char)

            out += char

        return out
