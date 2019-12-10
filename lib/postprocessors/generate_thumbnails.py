import os.path

import dhtmlparser
from PIL import Image

from .postprocessor_base import Postprocessor


class GenerateThumbnails(Postprocessor):
    @classmethod
    def postprocess(cls, dom, page, shared):
        dhtmlparser.makeDoubleLinked(dom)

        def path_that_handles_percents_and_spaces():
            dirname = os.path.dirname(page.path)

            if not os.path.exists(dirname) and r"%20" in dirname:
                dirname = dirname.replace(r"%20", " ")

            return os.path.join(shared._blog_root, dirname)

        for img in dom.find("img"):
            if not img.params.get("src"):
                print("Warning: image without src: " % img.tagToString())
                continue

            src = img.params["src"]
            if src.startswith("http://") or src.startswith("https://"):
                print("Warning: remote image: %s " % src)
                continue

            alt_style = img.parent.parent.parent.params.get("style", "")
            if "width:" in img.params.get("style", "") and "%" in img.params.get("style", ""):
                width = cls.parse_width(img)
                width = int(page.DEFAULT_WIDTH / 100.0 * width) + 5
            elif "width:" in alt_style and "%" in alt_style:
                width = cls.parse_width(img.parent.parent.parent)
                width = int(page.DEFAULT_WIDTH / 100.0 * width) + 5
            else:
                width = page.DEFAULT_WIDTH

            rel_image_path = src.replace(r"%20", " ")
            rel_thumb_path = cls.get_thumb_path(rel_image_path, img)
            abs_image_path = os.path.join(path_that_handles_percents_and_spaces(), rel_image_path)
            abs_thumb_path = os.path.join(path_that_handles_percents_and_spaces(), rel_thumb_path)

            try:
                cls.create_thumbnail(page, abs_image_path, abs_thumb_path, width)
                print("Generated thumbnail %s." % rel_thumb_path)
            except OSError as e:
                print("Can't convert %s: %s" % (abs_image_path, str(e)))
                continue

            img.params["src"] = rel_thumb_path

    @classmethod
    def get_thumb_path(cls, image_path, img_tag):
        thumb_dir = os.path.dirname(image_path)
        thumb_name = os.path.basename(img_tag.params["src"].replace("%20", " "))
        thumb_name = str(thumb_name).rsplit(".", 1)[0] + "_thumb.jpg"
        return os.path.join(thumb_dir, thumb_name)

    @classmethod
    def parse_width(cls, tag):
        widths = [
            elem.strip().split(":")[-1].replace("%", "")
            for elem in tag.params.get("style", "").split(";")
            if elem.strip().lower().startswith("width:") and elem.strip().lower().endswith("%")
        ]

        if not widths:
            return

        return float(widths[0])

    @classmethod
    def create_thumbnail(cls, page, abs_image_path, abs_thumb_path, width):
        img = Image.open(abs_image_path)

        if img.mode in ('RGBA', 'LA'):  # sigh..
            background = Image.new(img.mode[:-1], img.size, 'white')
            background.paste(img, img.split()[-1])
            img = background

        img.convert('RGB')

        if img.size[0] < page.DEFAULT_WIDTH:
            raise OSError("Already smaller than required.")

        height = img.size[1] * (img.size[0] / width)
        img.thumbnail((width, height), Image.ANTIALIAS)
        img.save(abs_thumb_path, "JPEG")
        img.close()
