from lib.settings import settings
from lib.virtual_fs import Data
from lib.virtual_fs import Directory
from lib.virtual_fs import VirtualFS

from .postprocessor_base import PostprocessorBase


class AddRobotsAndSitemap(PostprocessorBase):
    _sitemap_template = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{urls}
</urlset> 
"""
    _url_template_with_lastmod = """
  <url>
    <loc>{loc}</loc>
    <lastmod>{lastmod}</lastmod>
    <changefreq>{changefreq}</changefreq>
  </url>"""

    _url_template_without_lastmod = """
  <url>
    <loc>{loc}</loc>
  </url>"""

    _robots = """Sitemap: https://blog.rfox.eu/sitemap.xml"""

    @classmethod
    def postprocess(cls, virtual_fs: VirtualFS, root: Directory):
        settings.logger.info("Generating sitemap.xml and robots.txt..")

        sitemap_xml = Data("sitemap.xml", cls._create_sitemap(root).encode("utf-8"))
        robots_txt = Data("robots.txt", cls._robots.encode("utf-8"))

        for file in [sitemap_xml, robots_txt]:
            root.files.append(file)
            file.parent = root

    @classmethod
    def _create_sitemap(cls, root):
        url_snippets = "".join(x for x in cls._yield_page_xml_snippets(root))
        return cls._sitemap_template.format(urls=url_snippets)

    @classmethod
    def _yield_page_xml_snippets(cls, root):
        for page in root.walk_htmls():
            abs_url = cls._to_abs_url_path(page.path)

            # skip second index page
            if abs_url.endswith("index.html"):
                continue

            changefreq = "yearly"

            lastmod = page.metadata.date
            if page.metadata.last_mod is not None:
                lastmod = page.metadata.last_mod
                changefreq = "monthly"

            if lastmod:
                yield cls._url_template_with_lastmod.format(
                    loc=abs_url,
                    lastmod=lastmod.split(" ")[0],
                    changefreq=changefreq
                )
            else:
                yield cls._url_template_without_lastmod.format(loc=abs_url)
