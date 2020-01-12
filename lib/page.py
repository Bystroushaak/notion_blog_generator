import os
import copy

import sh
import dhtmlparser

from lib import postprocessors
from lib.shared_resources import SharedResources


class Page:
    DEFAULT_WIDTH = 900  # 900 is the max width on the page

    def __init__(self, path: str, content, shared: SharedResources):
        self.path = path
        self.content = content
        self.shared = shared
        self.dom = dhtmlparser.parseString(self.content)

        self.is_index = False

    @property
    def title(self):
        return self.dom.find("h1", {"class": "page-title"})[0].getContent()

    def save(self, blog_path):
        path = os.path.join(blog_path, self.path)

        dirname = os.path.dirname(path)
        if not os.path.exists(dirname):
            os.makedirs(dirname, exist_ok=True)

        with open(path, "w") as f:
            f.write(self.dom.__str__())

        try:
            sh.tidy("-m", "-w", "0", "-i", path)
        except:
            pass

        if self.is_index:
            self._save_also_index_page(path)

    def _save_also_index_page(self, path):
        full_path_without_filetype = path.rsplit(".", 1)[0]
        index_path = os.path.join(full_path_without_filetype, "index.html")
        dirname = full_path_without_filetype.rsplit("/", 1)[-1]

        if not os.path.exists(full_path_without_filetype):
            os.makedirs(full_path_without_filetype, exist_ok=True)

        dom = copy.copy(self.dom)

        self._fix_all_local_links(dom, dirname)

        is_root_index = os.path.abspath(full_path_without_filetype) == os.path.abspath(self.shared._real_blog_root)

        self._fix_breadcrumb_links(dom, is_root_index)

        # fix also style link
        if not is_root_index:
            style = dom.find("link", {"rel": "stylesheet"})[0]
            style.params["href"] = "../" + style.params["href"]

        # oh, and also images
        for img in dom.find("img"):
            if not img.params["src"].startswith("http"):
                img.params["src"] = "../" + img.params["src"]

        with open(index_path, "w") as f:
            f.write(dom.prettify())

    def _fix_all_local_links(self, dom, dirname):
        for a in dom.find("a"):
            if not "href" in a.params:
                continue

            # fixed later
            if a.params.get("class", "") == "breadcrumb":
                continue

            href = a.params["href"]
            if href.startswith(dirname):
                a.params["href"] = href.split("/", 1)[-1]

    def _fix_breadcrumb_links(self, dom, is_root_index):
        for a in dom.find("a"):
            if "href" not in a.params:
                continue

            href = a.params["href"]
            if href.startswith("http"):
                continue

            if is_root_index:
                href = href.split("/", 1)[-1]  # throw blog root from the beginning
            else:
                href = "../" + href

            a.params["href"] = href

    def postprocess(self):
        postprocessors_classes = [
            postprocessors.RemoveInlinedStyle,
            postprocessors.AddAtomFeed,
            postprocessors.AddFileIcons,
            postprocessors.AddBreadcrumb,
            postprocessors.AddPatreonButton,
            postprocessors.AddTwitterCard,
            postprocessors.FixNotionLinks,
            postprocessors.FixYoutubeEmbeds,
            postprocessors.AddAnalyticsTag,
            postprocessors.GenerateThumbnails,
            postprocessors.AddFavicon,
            postprocessors.PostprocessInlinedStyles,
            postprocessors.PostprocessChangelog,
            postprocessors.PostprocessIndex,
            postprocessors.AddSidebar,
            postprocessors.AddScriptsAndButtons,
        ]

        full_path_without_filetype = self.path.rsplit(".", 1)[0]
        for path in self.shared.all_pages.keys():
            if path.startswith(full_path_without_filetype + "/"):
                self.is_index = True
                break

        for postprocessor in postprocessors_classes:
            postprocessor.postprocess(self.dom, self, self.shared)

