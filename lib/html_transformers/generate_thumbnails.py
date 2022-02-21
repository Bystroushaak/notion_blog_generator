import io

import dhtmlparser3
from PIL import Image

from lib.settings import settings
from lib.settings import ThumbFormat
from lib.virtual_fs import Data
from lib.virtual_fs import HtmlPage
from lib.virtual_fs import VirtualFS
from lib.virtual_fs import Directory

from .transformer_base import TransformerBase


class SmallerThanRequired(UserWarning):
    pass


class GenerateThumbnails(TransformerBase):
    thumb_cache = None
    resource_registry = None

    @classmethod
    def log_transformer(cls):
        if settings.generate_thumbnails:
            settings.logger.info(
                "Generating %s thumbnails for all images..", settings.thumb_format
            )
        else:
            settings.logger.info("settings.generate_thumbnails == False")

    @classmethod
    def transform(cls, virtual_fs: VirtualFS, root: Directory, page: HtmlPage):
        if not settings.generate_thumbnails:
            return

        if cls.resource_registry is None:
            cls.resource_registry = virtual_fs.resource_registry

        for img in page.dom.find("img"):
            if "src" not in img:
                settings.logger.warning("Image without src: `%s`", img.to_string())
                continue

            src = img["src"]
            if src.startswith("http://") or src.startswith("https://"):
                continue

            cls._add_thumbnail_for_image(img, src)

    @classmethod
    def _add_thumbnail_for_image(cls, img_tag, src):
        img = cls.resource_registry.item_by_ref_str(src)
        if img.filename.lower().endswith(".svg"):
            return

        alt_style = img_tag.parent.parent.parent.parameters.get("style", "")
        img_tag_style = img_tag.parameters.get("style", "")
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
            img_tag["src"] = cls._get_ref_str_for_img(thumb)
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

        img_tag["src"] = cls._get_ref_str_for_img(thumb_img)
        cls._put_into_same_directory_as_img(img, thumb_img)

    @classmethod
    def parse_width(cls, tag):
        def width_percent(style):
            style = style.strip().lower()
            if not style.startswith("width:"):
                return False
            if not style.endswith("%"):
                return False
            return True

        widths = [
            styles.strip().split(":")[-1].replace("%", "")
            for styles in tag.parameters.get("style", "").split(";")
            if width_percent(styles)
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

        thumb_img = Data(full_img.original_path, content=thumb_img_as_io.getvalue())

        full_img_name_tokens = full_img.filename.rsplit(".", 1)
        suffix = ThumbFormat.thumb_format_to_suffix(settings.thumb_format)
        if len(full_img_name_tokens) == 2:
            name_base = full_img_name_tokens[0].strip()
            name_base = name_base.replace(" ", "_")
            thumb_img.filename = f"{name_base}_thumb.{suffix}"
        else:
            thumb_img.filename = f"{full_img.filename}_thumb.{suffix}"

        return thumb_img

    @classmethod
    def _generate_thumb_to_io(cls, full_img_as_io, width):
        img = Image.open(full_img_as_io)

        if img.mode in ("RGBA", "LA"):  # sigh..
            background = Image.new(img.mode[:-1], img.size, "white")
            background.paste(img, img.split()[-1])
            img = background

        img = img.convert("RGB")

        if img.size[0] < settings.page_width:
            raise SmallerThanRequired("Already smaller than required.")

        height = img.size[1] * (img.size[0] / width)
        img.thumbnail((width, height))

        thumb_img_as_io = io.BytesIO()
        img.save(thumb_img_as_io, settings.thumb_format)
        img.close()

        return thumb_img_as_io
