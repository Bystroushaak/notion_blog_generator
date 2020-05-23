import dhtmlparser

from lib.settings import settings

from .transformer_base import TransformerBase


class AddPatreonButton(TransformerBase):
    @classmethod
    def log_transformer(cls):
        settings.logger.info("Adding Patreon button to all pages..")

    @classmethod
    def transform(cls, virtual_fs, root, page):
        if not settings.patreon_url:
            return

        html_code = (
            '<div class="corner-ribbon top-right red">'
            '<a href="%s">Become a Patron</a>'
            '</div>'
        )
        button_tag = dhtmlparser.parseString(html_code % settings.patreon_url)

        page.dom.find("body")[0].childs.append(button_tag)
