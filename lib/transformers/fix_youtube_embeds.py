from urllib.parse import parse_qs
from urllib.parse import urlparse

import dhtmlparser

from .postprocessor_base import Postprocessor


class FixYoutubeEmbeds(Postprocessor):
    @classmethod
    def postprocess(cls, dom, page, shared):
        embed_code = (
            '<iframe width="100%%" height="50%%" frameborder="0" src="https://www.youtube.com/embed/%s"'
            'allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" '
            'allowfullscreen></iframe>\n\n'
        )

        youtube_links = dom.match(
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
                print("Unparsed alt video %s hash:%s" % (video_url, video_hash))

            html = embed_code % video_hash
            tag = dhtmlparser.parseString(html)

            link.replaceWith(tag)
