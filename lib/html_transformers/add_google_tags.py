import dhtmlparser

from lib.settings import settings
from lib.virtual_fs import HtmlPage
from lib.virtual_fs import VirtualFS
from lib.virtual_fs import Directory

from .transformer_base import TransformerBase


class AddGoogleTags(TransformerBase):
    analytics_code = """
    <!-- Global site tag (gtag.js) - Google Analytics -->
    <script src="https://www.googletagmanager.com/gtag/js?id=%s"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){dataLayer.push(arguments);}
      gtag('js', new Date());
    
      gtag('config', '%s');
    </script>
    """ % (settings.google_analytics_code, settings.google_analytics_code)
    analytics_tag = dhtmlparser.parseString(analytics_code)

    adsense_code = """<script data-ad-client="%s" src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js" async></script>"""
    adsense_tag = dhtmlparser.parseString(adsense_code % settings.google_adsense_code)

    top_vertical_ad_code = """
    <ins class="adsbygoogle"
     style="display:block"
     data-ad-client="ca-pub-8322439660353685"
     data-ad-slot="9175281399"
     data-ad-format="auto"
     data-full-width-responsive="true"></ins>
<script>(adsbygoogle = window.adsbygoogle || []).push({});</script>
"""

    in_article_vertical_ad_code = """
<ins class="adsbygoogle"
     style="display:block; text-align:center;"
     data-ad-layout="in-article"
     data-ad-format="fluid"
     data-ad-client="ca-pub-8322439660353685"
     data-ad-slot="8927869381"></ins>
<script>(adsbygoogle = window.adsbygoogle || []).push({});</script>
"""
    bottom_vertical_ad_code = """
    <ins class="adsbygoogle"
     style="display:block"
     data-ad-client="ca-pub-8322439660353685"
     data-ad-slot="4657737295"
     data-ad-format="auto"
     data-full-width-responsive="true"></ins>
<script>(adsbygoogle = window.adsbygoogle || []).push({});</script>
"""
    cookie_consent_code = """
<script src="https://cdn.jsdelivr.net/npm/cookieconsent@3/build/cookieconsent.min.js" data-cfasync="false"></script>
<script>
window.cookieconsent.initialise({
  "palette": {
    "popup": {
      "background": "#edeff5",
      "text": "#838391"
    },
    "button": {
      "background": "#4b81e8"
    }
  }
});
</script>
"""
    cookie_consent_css_code = """
  <link rel="stylesheet" type="text/css" href="https://cdn.jsdelivr.net/npm/cookieconsent@3/build/cookieconsent.min.css" />
"""
    cookie_consent_css_tag = dhtmlparser.parseString(cookie_consent_css_code)

    @classmethod
    def log_transformer(cls):
        settings.logger.info("Adding Google analytics & adsense tags to all pages..")

    @classmethod
    def transform(cls, virtual_fs: VirtualFS, root: Directory, page: HtmlPage):
        head = page.dom.find("head")[0]

        if settings.google_analytics_code:
            head.childs.append(cls.analytics_tag)

        if settings.google_adsense_code:
            head.childs.append(cls.adsense_tag)

        body = page.dom.find("body")[0]
        dhtmlparser.makeDoubleLinked(body)

        is_category_page = any((page.metadata.unroll_categories,
                                page.metadata.unroll_subpages,
                                page.metadata.unroll))

        p_tags = body.find("p")
        if len(p_tags) > 8 and not is_category_page:
            selected_tag = p_tags[4]

            h1_tags = body.find("h1")
            if len(h1_tags) > 4:
                selected_tag = h1_tags[2]

            cls._add_ad_before(selected_tag)
        else:
            top_vertical_ad_tag = dhtmlparser.parseString(cls.top_vertical_ad_code)
            body.childs.insert(0, top_vertical_ad_tag)

        bottom_vertical_ad_tag = dhtmlparser.parseString(cls.bottom_vertical_ad_code)
        body.childs.append(bottom_vertical_ad_tag)

        cookie_consent_tag = dhtmlparser.parseString(cls.cookie_consent_code)
        body.childs.append(cookie_consent_tag)
        head.childs.append(cls.cookie_consent_css_tag)

    @classmethod
    def _add_ad_before(cls, selected_tag):
        parent = selected_tag.parent
        index = parent.childs.index(selected_tag)

        in_article_ad_tag = dhtmlparser.parseString(cls.in_article_vertical_ad_code)
        parent.childs.insert(index, in_article_ad_tag)
