from urllib.parse import parse_qs
from urllib.parse import urlparse

import dhtmlparser

from lib.settings import settings
from lib.virtual_fs import HtmlPage
from lib.virtual_fs import VirtualFS
from lib.virtual_fs import Directory

from .transformer_base import TransformerBase


class FixYoutubeEmbeds(TransformerBase):
    embed_html = (
        '<iframe width="100%%" height="50%%" frameborder="0" src="https://www.youtube.com/embed/%s"'
        'allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" '
        'allowfullscreen></iframe>\n\n'
    )

    @classmethod
    def log_transformer(cls):
        settings.logger.info("Embedding youtube videos..")

    @classmethod
    def transform(cls, virtual_fs: VirtualFS, root: Directory, page: HtmlPage):
        youtube_links = page.dom.match(
            "figure",
            {"tag_name": "div", "params": {"class": "source"}},
            "a"
        )
        for link in youtube_links:
            video_url = link.params.get("href", "")
            if "youtu" not in video_url:
                continue

            if "?v=" in video_url or "&v=" in video_url:
                query = urlparse(video_url).query
                video_hash = parse_qs(query)["v"][0]

            elif "youtu.be" in video_url and "t=" in video_url and "&v=" not in video_url:
                parsed = urlparse(video_url)
                video_hash = parsed.path
                if video_hash.startswith("/"):
                    video_hash = video_hash[1:]

                if parsed.query:
                    video_hash += "?" + parsed.query.replace("t=", "start=")

            else:
                video_hash = urlparse(video_url).path[0]
                settings.logger.error("Unparsed alt video `%s` hash: `%s`",
                                      video_url, video_hash)

            html = cls.embed_html % video_hash
            tag = dhtmlparser.parseString(html)

            link.replaceWith(tag)
