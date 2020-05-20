import os.path

import dhtmlparser

from .postprocessor_base import Postprocessor


class AddTwitterCard(Postprocessor):
    @classmethod
    def postprocess(cls, dom, page, shared):
        summary_card = """
        <meta name="twitter:card" content="summary" />
        <meta name="twitter:site" content="@Bystroushaak" />
        <meta name="twitter:title" content="{title}" />
        <meta name="twitter:description" content="{description}" />
        """

        large_image_card_html = """
        <meta name="twitter:card" content="summary_large_image" />
        <meta name="twitter:site" content="@Bystroushaak" />
        <meta name="twitter:creator" content="@Bystroushaak" />
        <meta name="twitter:title" content="{title}" />
        <meta name="twitter:description" content="{description}" />
        <meta name="twitter:image" content="{image}" />
        """

        dhtmlparser.makeDoubleLinked(dom)

        p_tags = dom.match(
            "body",
            {"tag_name": "div", "params": {"class": "page-body"}},
            "p"
        )
        possible_descriptions = [
            dhtmlparser.removeTags(p.getContent()) for p in p_tags
            if not p.find("time") and p.params.get("class") != "column" and \
            len(dhtmlparser.removeTags(p.getContent())) > 30 and p.parent.params.get("class") == "page-body"
        ]
        description = ""
        if possible_descriptions:
            description = possible_descriptions[0]

        if not description:
            return

        if dom.find("img"):
            first_image_path = dom.find("img")[0].params["src"]

            if first_image_path.startswith("http://") or first_image_path.startswith("https://"):
                full_img_path = first_image_path
            else:  # local path
                full_img_path = os.path.join(os.path.dirname(page.path), first_image_path)
                full_img_path = "http://blog.rfox.eu/" + full_img_path.replace(" ", "%20")

            meta_html = large_image_card_html.format(
                title=page.title,
                description=description,
                image=full_img_path
            )
        else:
            meta_html = summary_card.format(
                title=page.title,
                description=description,
            )

        meta_tags = dhtmlparser.parseString(meta_html)

        dom.find("head")[0].childs.extend(meta_tags.find("meta"))
