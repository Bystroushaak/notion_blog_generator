from notion_blog_generator.settings import settings
from notion_blog_generator.virtual_fs import Tags
from notion_blog_generator.virtual_fs import HtmlPage
from notion_blog_generator.virtual_fs import VirtualFS
from notion_blog_generator.virtual_fs import Directory
from notion_blog_generator.virtual_fs import RootSection

from notion_blog_generator.preprocessors import MakeRootSections
from notion_blog_generator.preprocessors.preprocessor_base import PreprocessorBase

TAG_PAGE_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
  <title>Tag: {tag_name}</title>
  <style></style>
</head>
<body>
  <article class="page sans tag-page">
    <header>
      <div class="page-header-icon undefined">
        <span class="icon">📂</span>
      </div>
      <h1 class="page-title">Tag: {tag_name}</h1>
    </header>
    <p class="tag-count">{count_label}</p>
    <div class="page-body">
        {links}
    </div>
  </article>
</body>
</html>
"""

TAG_INDEX_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
  <title>{title}</title>
  <style></style>
</head>
<body>
  <article class="page sans tag-index-page">
    <header>
      <div class="page-header-icon undefined">
        <span class="icon">📂</span>
      </div>
      <h1 class="page-title">{title}</h1>
    </header>
    <p class="tag-count">{count_label}</p>
    <div class="page-body">
        {links}
    </div>
  </article>
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

    MIN_TAG_USAGE = 2

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
            if len(subpages) < cls.MIN_TAG_USAGE:
                continue

            links = cls._yield_links_to_subpages(registry, subpages)

            count_label = cls._count_label(len(subpages), tag_manager.dirname)
            tag_page_html = TAG_PAGE_TEMPLATE.format(
                tag_name=tag,
                count_label=count_label,
                links="\n".join(list(links)),
            )

            tag_page = HtmlPage(tag_page_html, tag + ".html")
            tag_page.alt_title = tag
            tag_directory.add_file(tag_page)

            tag_ref_str = registry.register_item_as_ref_str(tag_page)
            tag_to_ref_str_map[tag] = tag_ref_str

        links_and_count = []
        for tag, tag_ref in tag_to_ref_str_map.items():
            no_items = len(tag_manager.tag_dict[tag])
            description = ('<p class="tag-entry-meta">'
                           + cls._count_label(no_items, tag_manager.dirname)
                           + "</p>")
            link = LINK_TEMPLATE.format(page_name=tag, ref_str=tag_ref,
                                        no_tags="",
                                        description=description)
            links_and_count.append((link, no_items))

        # sort by tag count
        links = (link for link, count in sorted(links_and_count, key=lambda x: x[1], reverse=True))

        # generate the tag index page
        tag_index_html = TAG_INDEX_TEMPLATE.format(
            title=tag_manager.alt_title,
            count_label=cls._tags_total_label(len(tag_to_ref_str_map),
                                              tag_manager.dirname),
            links="\n".join(links),
        )
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

            meta_parts = []
            if page.metadata.date:
                meta_parts.append(page.metadata.date)
            cat_link = cls._get_category_link(page, registry)
            if cat_link:
                meta_parts.append(cat_link)

            description = ""
            if meta_parts:
                description = ('<p class="tag-entry-meta">'
                               + " \u00B7 ".join(meta_parts) + "</p>")
            if page.metadata.page_description:
                description += "<p>" + page.metadata.page_description + "</p>"

            yield LINK_TEMPLATE.format(page_name=page.title, ref_str=ref_str,
                                       no_tags="", description=description)

    @classmethod
    def _get_category_link(cls, page, registry):
        if not page.parent or isinstance(page.parent, RootSection):
            return None

        current = page.parent
        while current.parent is not None and not isinstance(current.parent, RootSection):
            current = current.parent

        if not isinstance(current.parent, RootSection):
            return None
        if current.outer_index is None:
            return None

        cat_ref = registry.register_item_as_ref_str(current.outer_index)
        cat_name = current.filename.replace("_", " ")
        return '<a href="%s">%s</a>' % (cat_ref, cat_name)

    @classmethod
    def _count_label(cls, n, dirname):
        if dirname == "Tagy":
            if n == 1:
                return "%d článek" % n
            if 2 <= n <= 4:
                return "%d články" % n
            return "%d článků" % n
        return "%d article" % n if n == 1 else "%d articles" % n

    @classmethod
    def _tags_total_label(cls, n, dirname):
        if dirname == "Tagy":
            if n == 1:
                return "%d tag" % n
            if 2 <= n <= 4:
                return "%d tagy" % n
            return "%d tagů" % n
        return "%d tag" % n if n == 1 else "%d tags" % n

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

        all_tags = []
        for tag in sorted(tags):
            tag_ref = tag_to_ref_str_map.get(tag.lower())
            if tag_ref is None:
                continue
            tag_html = '<a href="{tag_ref}">{tag_name}</a>'
            tag_html = tag_html.format(tag_ref=tag_ref, tag_name=tag)
            all_tags.append(tag_html)

        if not all_tags:
            return ""

        out = "<hr><div><h3>%s</h3><p>" % title
        out += ", ".join(all_tags)
        out += "</p></div>"

        return out
