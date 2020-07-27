import os.path
from html import unescape
from urllib.parse import unquote
from functools import lru_cache

import sh
import yaml
import dhtmlparser

from lib.settings import settings

from lib.virtual_fs.file_baseclass import FileBase
from lib.virtual_fs.resource_registry import ResourceRegistry


class Metadata:
    def __init__(self):
        self.page_description = ""
        self.image_index = 0
        self.tags = []

        self.unroll = False
        self.unroll_description = False
        self.unroll_subpages = False
        self.unroll_length = settings.number_of_subpages_in_unroll

        self.date = None
        self.last_mod = None

        self.refs_from_other_pages = set()

    @classmethod
    def from_yaml(cls, yaml_str):
        data = yaml.load(yaml_str)
        if data is None:
            data = {}

        metadata = Metadata()

        alt_descr = data.get("Description", metadata.page_description)
        metadata.page_description = data.get("description", alt_descr)

        if isinstance(metadata.page_description, dict):
            key = list(metadata.page_description.keys())[0]
            val = metadata.page_description[key]
            metadata.page_description = key + ": " + val

        alt_index = data.get("image-index", metadata.image_index)
        metadata.image_index = data.get("image_index", alt_index)

        tags = data.get("tags")
        if tags:
            metadata.tags = [tag.strip() for tag in tags.split(",")]

        date = data.get("date")
        if date:
            metadata.date = date.replace("/", "-")

        last_mod = data.get("last-mod")
        if last_mod:
            metadata.last_mod = last_mod.replace("/", "-")

        metadata.unroll = data.get("unroll", metadata.unroll)
        metadata.unroll_description = data.get("unroll-description",
                                               metadata.unroll_description)
        metadata.unroll_subpages = data.get("unroll-subpages",
                                            metadata.unroll_subpages)
        metadata.unroll_length = data.get("unroll-len", metadata.unroll_length)
        metadata.unroll_length = data.get("unroll-length", metadata.unroll_length)

        return metadata

    def create_copy(self):
        metadata = Metadata()

        metadata.page_description = self.page_description
        metadata.image_index = self.image_index
        metadata.tags = self.tags

        metadata.unroll = self.unroll
        metadata.unroll_description = self.unroll_description
        metadata.unroll_subpages = self.unroll_subpages

        metadata.date = self.date
        metadata.last_mod = self.last_mod

        # metadata.refs_from_other_pages = set(self.refs_from_other_pages)

        return metadata


class HtmlPage(FileBase):
    def __init__(self, content, original_fn=None):
        super().__init__()

        self.content = content
        self.dom = dhtmlparser.parseString(self.content)

        self.original_fn = os.path.basename(original_fn)
        self.filename = self.original_fn
        self.hash = self._parse_hash(self.original_fn)

        self.metadata = Metadata()
        self.alt_title = None

        self.is_index_to = None

    def __repr__(self):
        return "HtmlPage(%s)" % self.filename

    @property
    def is_html(self):
        return True

    @property
    def is_index(self):
        return bool(self.is_index_to)

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
        return dhtmlparser.removeTags(title_el.__str__()).strip()

    def _parse_hash(self, notion_fn):
        without_html = notion_fn.rsplit(".", 1)[0]
        hash_without_name = without_html.split()[-1]

        return hash_without_name.strip()

    def convert_resources_to_ids(self, path_id_map):
        resources = self._collect_resources()

        for resource_generator, src in resources:
            for resource_el in resource_generator:
                if not resource_el.isTag():
                    continue

                resource_path = resource_el.params[src]
                dirname = os.path.dirname(self.path)
                full_resource_path = os.path.join(dirname, resource_path)
                abs_path = os.path.abspath(full_resource_path)

                try:
                    id = path_id_map[abs_path]
                    resource_el.params[src] = ResourceRegistry.as_ref_str(id)
                except KeyError:
                    unquoted = unquote(abs_path)
                    unquoted = unescape(unquoted)
                    try:
                        id = path_id_map[unquoted]
                        resource_el.params[src] = ResourceRegistry.as_ref_str(id)
                    except KeyError:
                        settings.logger.error("%s: Link not found, skipping: %s",
                                              self.filename, unquoted)
                        continue

    def convert_resources_to_paths(self, resource_registry: ResourceRegistry):
        resources = self._collect_resources()

        html_dir = os.path.dirname(self.path)

        for resource_generator, src in resources:
            for resource_el in resource_generator:
                if not resource_el.isTag():
                    continue

                resource_id_token = resource_el.params[src]

                if "://" in resource_id_token:
                    continue

                if not ResourceRegistry.is_ref_str(resource_id_token):
                    continue

                resource = resource_registry.item_by_ref_str(resource_id_token)
                resource_relpath = os.path.relpath(resource.path, html_dir)
                resource_el.params[src] = resource_relpath

                # add title= to <a> for better SEO
                if resource_el.getTagName() == "a":
                    if resource.is_html:
                        resource_el.params["title"] = resource.title
                    else:
                        resource_el.params["title"] = resource.filename

    def _collect_resources(self):
        links = self._collect_local_links()

        images = (img for img in self.dom.find("img")
                  if "://" not in img.params.get("src", ""))

        meta_links = (link for link in self.dom.find("link")
                      if "href" in link.params and \
                         "://" not in link.params.get("href", ""))
        scripts = (script for script in self.dom.find("script")
                   if "src" in script.params and \
                      "://" not in script.params.get("href", ""))
        twitter_images = (meta for meta in self.dom.find("meta",
                                                     {"name": "twitter:image"})
                          if "://" not in meta.params.get("content", ""))

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
                if "://" not in a.params.get("href", ""))

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
        copy = HtmlPage(
            self.dom.__str__(),
            self.original_fn,
        )
        copy.filename = self.filename
        copy.is_index_to = self.is_index_to
        copy.metadata = self.metadata.create_copy()

        return copy

    @property
    def root_section(self):
        if self.is_index_to is not None:
            return self.is_index_to.root_section

        return self.parent.root_section
