import time

import dhtmlparser

from lib.settings import settings
from lib.virtual_fs import Directory
from lib.virtual_fs import VirtualFS

from .postprocessor_base import PostprocessorBase


class AddMetadataToRoot(PostprocessorBase):
    @classmethod
    def postprocess(cls, virtual_fs: VirtualFS, root: Directory):
        settings.logger.info("Adding metadata to root index page..")

        root_index_page = root.inner_index

        body_container = root_index_page.dom.find("h1")[-1].parent

        meta_info_html = f"""
        <h1>Meta</h1>
        <ul>
            <li>Generated: {time.strftime("%Y-%m-%d %H:%M")}</li>
            <li>Generator: <a href="https://github.com/Bystroushaak/notion_blog_generator">https://github.com/Bystroushaak/notion_blog_generator</a></li>
        </ul>
        <span style="visibility: hidden;">m0wFG3PRCoJVTs7JcgBwsOXb3U7yPxBB</span>
        """

        body_container.childs.append(dhtmlparser.parseString(meta_info_html))
