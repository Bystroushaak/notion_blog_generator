import copy
import os.path
from html import unescape
from urllib.parse import unquote
from functools import lru_cache

import sh
import dhtmlparser3

from lib.settings import settings

from lib.virtual_fs.sidebar import Sidebar
from lib.virtual_fs.metadata import Metadata
from lib.virtual_fs.file_baseclass import FileBase
from lib.virtual_fs.resource_registry import ResourceRegistry


class HtmlPage(FileBase):
    def __init__(self, content, original_fn=None):
        super().__init__()

        self.content = content.replace("🗎", "📄")
        self.dom = dhtmlparser3.parse(self.content)

        self.original_fn = os.path.basename(original_fn)
        self.filename = self.original_fn
        self.hash = self._parse_hash(self.original_fn)

        self.metadata = Metadata()
        self.alt_title = None
        self.sidebar = Sidebar()  # may be replaced with None in add_sidebars.py!

        self.is_index_to = None

    def __repr__(self):
        return "HtmlPage(%s)" % self.filename

    @staticmethod
    def normalize_block_id(block_id):
        without_dashes = "".join([x for x in block_id if x != "-"])
        correctly_formatted = "%s-%s-%s-%s-%s" % (
            without_dashes[0:8],
            without_dashes[8:12],
            without_dashes[12:16],
            without_dashes[16:20],
            without_dashes[20:],
        )
        return correctly_formatted

    @property
    def pretty_hash(self):
        return self.normalize_block_id(self.hash)

    @property
    def is_html(self):
        return True

    @property
    def is_index(self):
        return bool(self.is_index_to)

    @property
    def is_category(self):
        if self.is_index_to:
            if self.is_index_to.subdirs:
                return True

            htmls = [file for file in self.is_index_to.walk_htmls()
                     if not file.is_index]
            if htmls:
                return True

        return False

    @property
    def icon(self):
        if self.is_category:
            return "📂"

        return "📄"

    @property
    @lru_cache()
    def is_embeddable(self):
        root = self.get_root_dir()
        if self is root.outer_index or self is root.inner_index:
            return False

        if len(self.dom.find("img")) > 3:
            return True

        # pages that are indexes in directories that just contain images
        # can't be considered index pages..
        if self.is_index:
            subpages = [x for x in self.is_index_to.files if x.is_html]
            if len(subpages) <= 1:
                return True

        # if self.is_index and len(self.dom.find("article").__str__()) < 15000:
        #     return False

        return True

    @property
    def title(self):
        if self.alt_title:
            return self.alt_title

        title_el = self.dom.find("h1", {"class": "page-title"})[0]
        return title_el.content_without_tags().strip()

    def _parse_hash(self, notion_fn):
        without_html_suffix = notion_fn.rsplit(".", 1)[0]
        hash_without_name = without_html_suffix.split()[-1]

        return hash_without_name.strip()

    def convert_resources_to_ids(self, path_id_map):
        resources = self._collect_resources()

        for resource_generator, src in resources:
            for resource_el in resource_generator:
                if not isinstance(resource_el, dhtmlparser3.Tag):
                    continue

                resource_path = resource_el[src]
                dirname = os.path.dirname(self.path)
                full_resource_path = os.path.join(dirname, resource_path)
                abs_path = os.path.abspath(full_resource_path)

                try:
                    id = path_id_map[abs_path]
                    resource_el[src] = ResourceRegistry.as_ref_str(id)
                except KeyError:
                    unquoted = unquote(abs_path)
                    unquoted = unescape(unquoted)
                    try:
                        id = path_id_map[unquoted]
                        resource_el[src] = ResourceRegistry.as_ref_str(id)
                    except KeyError:
                        settings.logger.error("%s: Link not found, skipping: %s",
                                              self.filename, unquoted)
                        continue

    def convert_resources_to_paths(self, resource_registry: ResourceRegistry):
        resources = self._collect_resources()

        html_dir = os.path.dirname(self.path)

        for resource_generator, src in resources:
            for resource_el in resource_generator:
                if not isinstance(resource_el, dhtmlparser3.Tag):
                    continue

                resource_id_token = resource_el[src]

                if "://" in resource_id_token:
                    continue

                if not ResourceRegistry.is_ref_str(resource_id_token):
                    continue

                resource = resource_registry.item_by_ref_str(resource_id_token)
                resource_relpath = os.path.relpath(resource.path, html_dir)
                resource_el[src] = resource_relpath

                # add title= to <a> for better SEO
                if resource_el.name == "a":
                    if resource.is_html:
                        resource_el["title"] = resource.title
                    else:
                        resource_el["title"] = resource.filename

    def _collect_resources(self):
        links = self._collect_local_links()

        images = (img for img in self.dom.find("img")
                  if "://" not in img)

        meta_links = (link for link in self.dom.find("link")
                      if "href" in link and \
                         "://" not in link.parameters.get("href", ""))
        scripts = (script for script in self.dom.find("script")
                   if "src" in script and \
                      "://" not in script.parameters.get("href", ""))
        twitter_images = (meta for meta in self.dom.find("meta",
                                                     {"name": "twitter:image"})
                          if "://" not in meta.parameters.get("content", ""))

        resources = (
            (links, "href"),
            (images, "src"),
            (meta_links, "href"),
            (scripts, "src"),
            (twitter_images, "content"),
        )

        return resources

    def _collect_local_links(self):
        return (a for a in self.dom.find("a")
                if "://" not in a.parameters.get("href", ""))

    def save_as(self, file_path):
        with open(file_path, "wt") as f:
            if settings.write_prettify:
                f.write(self.dom.prettify())
            else:
                f.write(self.dom.__str__())

        if settings.tidy_html:
            try:
                sh.tidy("-m", "-w", "0", "-i", file_path)
            except:
                pass

    def create_copy(self):
        page_copy = HtmlPage("", self.original_fn)
        page_copy.content = self.content
        page_copy.dom = copy.deepcopy(self.dom)
        page_copy.filename = self.filename
        page_copy.hash = self.hash
        page_copy.original_fn = self.original_fn
        page_copy.is_index_to = self.is_index_to
        page_copy.alt_title = self.alt_title

        page_copy.metadata = self.metadata.create_copy()
        page_copy.sidebar = self.sidebar

        return page_copy

    @property
    def root_section(self):
        if self.is_index_to is not None:
            return self.is_index_to.root_section

        return self.parent.root_section
