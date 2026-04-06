import time

import dhtmlparser3

from notion_blog_generator.settings import settings
from notion_blog_generator.virtual_fs import Directory
from notion_blog_generator.virtual_fs import VirtualFS

from .postprocessor_base import PostprocessorBase


class AddMetadataToRoot(PostprocessorBase):
    @classmethod
    def postprocess(cls, virtual_fs: VirtualFS, root: Directory):
        settings.logger.info("Adding metadata to root index page..")

        root_index_page = root.inner_index

        # Find the last div with class "page-body" content
        page_body = root_index_page.dom.find("div", {"class": "page-body"})
        if not page_body:
            settings.logger.warning("Could not find page-body in root index!")
            return

        body_container = page_body[0]

        meta_info_html = f"""
        <h1>Meta</h1>
        <ul>
            <li>Generated: {time.strftime("%Y-%m-%d %H:%M")}</li>
            <li>Generator: <a href="https://github.com/Bystroushaak/notion_blog_generator">https://github.com/Bystroushaak/notion_blog_generator</a></li>
        </ul>
        <span style="visibility: hidden;">m0wFG3PRCoJVTs7JcgBwsOXb3U7yPxBB</span>
        """

        body_container[-1:] = dhtmlparser3.parse(meta_info_html)
