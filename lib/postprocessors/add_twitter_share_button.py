import dhtmlparser

from .postprocessor_base import Postprocessor


class AddTwitterShareButton(Postprocessor):
    @classmethod
    def postprocess(cls, dom, page, shared):
        twitter_load_script = """<script src="/twitter_script.js"></script>"""

        twitter_share_button = """
<a class="twitter-share-button" id="twitter_button" href="#"><img src="/tweet_button.png" /></a>
        """

        if page.is_index and len(dom.__str__()) < 15000:
            return

        head = dom.find("head")[0]
        head.childs.append(dhtmlparser.parseString(twitter_load_script))

        body_tag = dom.find("body")[0]
        body_tag.childs.append(dhtmlparser.parseString(twitter_share_button))

        body_tag.params["onload"] = "add_twitter_link();"
