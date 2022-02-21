from urllib.parse import parse_qs
from urllib.parse import urlparse

import dhtmlparser3

from lib.settings import settings
from lib.virtual_fs import HtmlPage
from lib.virtual_fs import VirtualFS
from lib.virtual_fs import Directory

from .transformer_base import TransformerBase


class FixYoutubeEmbeds(TransformerBase):
    @classmethod
    def log_transformer(cls):
        settings.logger.info("Embedding youtube videos..")

    @classmethod
    def transform(cls, virtual_fs: VirtualFS, root: Directory, page: HtmlPage):
        youtube_links = page.dom.match(
            "figure",
            ["div", {"class": "source"}],
            "a"
        )
        for link in youtube_links:
            video_url = link.parameters.get("href", "")
            if "youtu" not in video_url:
                continue

            try:
                video_hash = cls._parse_yt_embed_url(video_url)
            except TypeError:
                video_hash = urlparse(video_url).path[0]
                settings.logger.error("Unparsed alt video `%s` hash: `%s`",
                                      video_url, video_hash)

            video_tag = dhtmlparser3.Tag(
                "iframe",
                parameters={
                    "width": "100%",
                    "height": "50%",
                    "frameborder": "0",
                    "src": f"https://www.youtube.com/embed/{video_hash}",
                    "allow": "accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture",
                    "allowfullscreen": "",
                }
            )

            link.replace_with(video_tag)

    @classmethod
    def _parse_yt_embed_url(cls, video_url):
        video_url = video_url.replace("&amp;", "&")
        video_url = video_url.replace("#t=", "&t=")

        if "?v=" in video_url or "&v=" in video_url:
            query_str = urlparse(video_url).query
            parsed_query = parse_qs(query_str)
            video_hash = parsed_query["v"][0]

            if "t" in parsed_query:
                video_hash += "?start=" + parsed_query["t"][0]

            return video_hash

        if "youtu.be" in video_url and "t=" in video_url and "&v=" not in video_url:
            parsed = urlparse(video_url)
            video_hash = parsed.path
            if video_hash.startswith("/"):
                video_hash = video_hash[1:]

            if parsed.query:
                video_hash += "?" + parsed.query.replace("t=", "start=")

            return video_hash

        raise TypeError("Can't parse URL: %s" % video_url, video_url)
