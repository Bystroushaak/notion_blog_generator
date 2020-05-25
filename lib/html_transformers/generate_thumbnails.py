import io

import dhtmlparser
from PIL import Image

from lib.settings import settings
from ..virtual_fs import Data

from .transformer_base import TransformerBase


class SmallerThanRequired(UserWarning):
    pass


class GenerateThumbnails(TransformerBase):
    thumb_cache = None
    resource_registry = None

    @classmethod
    def log_transformer(cls):
        settings.logger.info("Generating thumbnails for all images..")

    @classmethod
    def transform(cls, virtual_fs, root, page):
        if cls.resource_registry is None:
            cls.resource_registry = virtual_fs.resource_registry

        dhtmlparser.makeDoubleLinked(page.dom)

        for img in page.dom.find("img"):
            if not img.params.get("src"):
                settings.logger.warning("Image without src: `%s`", img.tagToString())
                continue

            src = img.params["src"]
            if src.startswith("http://") or src.startswith("https://"):
                continue

            cls._add_thumbnail_for_image(img, src)

    @classmethod
    def _add_thumbnail_for_image(cls, img_tag, src):
        img = cls.resource_registry.item_by_ref_str(src)
        if img.filename.lower().endswith(".svg"):
            return

        alt_style = img_tag.parent.parent.parent.params.get("style", "")
        img_tag_style = img_tag.params.get("style", "")
        if "width:" in img_tag_style and "%" in img_tag_style:
            width = cls.parse_width(img_tag)
            width = int(settings.page_width / 100.0 * width) + 5
        elif "width:" in alt_style and "%" in alt_style:
            width = cls.parse_width(img_tag.parent.parent.parent)
            width = int(settings.page_width / 100.0 * width) + 5
        else:
            width = settings.page_width

        thumb = None
        if cls.thumb_cache:
            thumb = cls.thumb_cache.try_restore(img)

        if thumb is not None:
            settings.logger.debug("Thumbnail `%s` found in cache.", img.path)
            img_tag.params["src"] = cls._get_ref_str_for_img(thumb)
            cls._put_into_same_directory_as_img(img, thumb)
            return

        try:
            settings.logger.debug("Generating thumbnail for %s.", img.path)
            thumb_img = cls._generate_thumbnail(img, width)
        except SmallerThanRequired:
            return
        except OSError as e:
            settings.logger.exception("Can't convert %s: %s", img.path, str(e))
            return

        img_tag.params["src"] = cls._get_ref_str_for_img(thumb_img)
        cls._put_into_same_directory_as_img(img, thumb_img)


    @classmethod
    def parse_width(cls, tag):
        widths = [
            elem.strip().split(":")[-1].replace("%", "")
            for elem in tag.params.get("style", "").split(";")
            if elem.strip().lower().startswith("width:") \
               and elem.strip().lower().endswith("%")
        ]

        if not widths:
            return

        return float(widths[0])

    @classmethod
    def _get_ref_str_for_img(cls, thumb_img):
        return cls.resource_registry.register_item_as_ref_str(thumb_img)

    @classmethod
    def _put_into_same_directory_as_img(cls, img, thumb):
        directory = img.parent
        directory.add_file(thumb)

    @classmethod
    def _generate_thumbnail(cls, full_img: Data, width: int):
        full_img_as_io = io.BytesIO(full_img.content)
        full_img_as_io.name = full_img.filename

        thumb_img_as_io = cls._generate_thumb_to_io(full_img_as_io, width)

        thumb_img = Data(full_img.original_path,
                         content=thumb_img_as_io.getvalue())

        full_img_name_tokens = full_img.filename.rsplit(".", 1)
        if len(full_img_name_tokens) == 2:
            name_base = full_img_name_tokens[0].strip()
            name_base = name_base.replace(" ", "_")
            thumb_img.filename = "%s_thumb.jpg" % name_base
        else:
            thumb_img.filename = full_img.filename + "_thumb"

        return thumb_img

    @classmethod
    def _generate_thumb_to_io(cls, full_img_as_io, width):
        img = Image.open(full_img_as_io)

        if img.mode in ('RGBA', 'LA'):  # sigh..
            background = Image.new(img.mode[:-1], img.size, 'white')
            background.paste(img, img.split()[-1])
            img = background

        img = img.convert('RGB')

        if img.size[0] < settings.page_width:
            raise SmallerThanRequired("Already smaller than required.")

        height = img.size[1] * (img.size[0] / width)
        img.thumbnail((width, height), Image.ANTIALIAS)

        thumb_img_as_io = io.BytesIO()
        img.save(thumb_img_as_io, "JPEG")
        img.close()

        return thumb_img_as_io
