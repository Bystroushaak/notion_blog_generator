from lib.settings import settings
from lib.virtual_fs import Tags
from lib.virtual_fs import HtmlPage
from lib.virtual_fs import VirtualFS
from lib.virtual_fs import Directory

from lib.preprocessors import MakeRootSections
from lib.preprocessors.preprocessor_base import PreprocessorBase

TAG_PAGE_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
  <title>List of pages for `{tag_name}`</title>
  <style></style>
</head>
<body>
  <article class="page sans">
    <header>
      <div class="page-header-icon undefined">
        <span class="icon">📂</span>
      </div>
      <h1 class="page-title">List of pages with `{tag_name}` tag</h1>
    </header>
    <div class="page-body">
        {links}
    </div>
</body>
</html>
"""

TAG_INDEX_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
  <title>Tags</title>
  <style></style>
</head>
<body>
  <article class="page sans">
    <header>
      <div class="page-header-icon undefined">
        <span class="icon">📂</span>
      </div>
      <h1 class="page-title">Tags used in the blogs</h1>
    </header>
    <div class="page-body">
        {links}
    </div>
</body>
</html>
"""

LINK_TEMPLATE = """
      <figure class="link-to-page">
        <h3><a href="{ref_str}"><span class="icon">🗎</span>{page_name}</a> {no_tags}</h3>
        {description}
      </figure>
"""


class GenerateTagStructure(PreprocessorBase):
    requires = [MakeRootSections]

    @classmethod
    def preprocess(cls, virtual_fs: VirtualFS, root: Directory):
        settings.logger.info("Collecting tags..")

        registry = virtual_fs.resource_registry
        Tags._collect_tags(root)

        settings.logger.info("Generating tag structure..")

        for root_section in root.get_root_sections():
            tag_to_ref_str_map = cls._generate_tag_structure(root, registry,
                                                             root_section.tags)

            settings.logger.info("Putting taglist to pages with tags..")
            cls._add_tags_to_all_pages(root_section.tags, tag_to_ref_str_map)

    @classmethod
    def _generate_tag_structure(cls, root, registry, tag_manager):
        tag_directory = Directory(tag_manager.dirname)
        tag_to_ref_str_map = {}
        for tag, subpages in sorted(tag_manager.tag_dict.items()):
            links = cls._yield_links_to_subpages(registry, subpages)

            tag_page_html = TAG_PAGE_TEMPLATE.format(tag_name=tag,
                                                     links="\n".join(list(links)))

            tag_page = HtmlPage(tag_page_html, tag + ".html")
            tag_page.alt_title = tag
            tag_directory.add_file(tag_page)

            tag_ref_str = registry.register_item_as_ref_str(tag_page)
            tag_to_ref_str_map[tag] = tag_ref_str

        links = []
        for tag, tag_ref in tag_to_ref_str_map.items():
            no_items = len(tag_manager.tag_dict[tag])
            no_tags = "(%s items)" if no_items > 1 else "(%s item)"
            links.append(LINK_TEMPLATE.format(page_name=tag, ref_str=tag_ref,
                                              no_tags=no_tags % no_items,
                                              description=""))

        tag_index_html = TAG_INDEX_TEMPLATE.format(links="\n".join(links))
        tag_index_outer = HtmlPage(tag_index_html, "%s.html" % tag_manager.dirname)
        tag_index_outer.alt_title = tag_manager.alt_title

        root.add_subdir(tag_directory)
        root.add_file(tag_index_outer)

        tag_directory.add_copy_as_index(tag_index_outer)

        return tag_to_ref_str_map

    @classmethod
    def _yield_links_to_subpages(cls, registry, subpages):
        subpages_sorted = sorted(subpages, reverse=True,
                                 key=lambda x: x.metadata.date or x.title)

        for page in subpages_sorted:
            ref_str = registry.register_item_as_ref_str(page)
            description = "<p>" + page.metadata.page_description + "</p><hr>"
            yield LINK_TEMPLATE.format(page_name=page.title, ref_str=ref_str,
                                       no_tags="", description=description)

    @classmethod
    def _add_tags_to_all_pages(cls, tag_manager, tag_to_ref_str_map):
        for page in tag_manager.pages_with_tags:
            body = page.dom.find("body")[0]
            tag_box_html = cls._get_tagbox(tag_manager.dirname, page.metadata.tags,
                                           tag_to_ref_str_map)

            page.sidebar.tagbox_html = tag_box_html

    @classmethod
    def _get_tagbox(cls, title, tags, tag_to_ref_str_map):
        if not tags:
            return ""

        out = "<hr><div><h3>%s</h3><p>" % title
        all_tags = []
        for tag in sorted(tags):
            tag_html = '<a href="{tag_ref}">{tag_name}</a>'
            tag_html = tag_html.format(tag_ref=tag_to_ref_str_map[tag.lower()],
                                       tag_name=tag)
            all_tags.append(tag_html)

        out += ", ".join(all_tags)
        out += "</p></div>"

        return out
