import os
import copy

import dhtmlparser

from lib import postprocessors
from lib import SharedResources


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
            f.write(self.dom.prettify())

        if self.is_index:
            self._save_also_index_page(path)

    def _save_also_index_page(self, path):
        full_path_without_filetype = path.rsplit(".", 1)[0]
        index_path = os.path.join(full_path_without_filetype, "index.html")
        dirname = full_path_without_filetype.rsplit("/", 1)[-1]

        if not os.path.exists(full_path_without_filetype):
            os.makedirs(full_path_without_filetype, exist_ok=True)

        # fix all local links
        dom = copy.copy(self.dom)
        for a in dom.find("a"):
            if not "href" in a.params:
                continue

            # fixed later
            if a.params.get("class", "") == "breadcrumb":
                continue

            href = a.params["href"]
            if href.startswith(dirname):
                a.params["href"] = href.split("/", 1)[-1]

        # fix breadcrumb links
        for a in dom.find("a", {"class": 'breadcrumb'}):
            if not a.params["href"].startswith("http"):
                a.params["href"] = "../" + a.params["href"]

        # fix also style link
        style = dom.find("link", {"rel": "stylesheet"})[0]
        style.params["href"] = "../" + style.params["href"]

        # oh, and also images
        for img in dom.find("img"):
            if not img.params["src"].startswith("http"):
                img.params["src"] = "../" + img.params["src"]

        with open(index_path, "w") as f:
            f.write(dom.prettify())

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
        ]

        for postprocessor in postprocessors_classes:
            postprocessor.postprocess(self.dom, self, self.shared)

        full_path_without_filetype = self.path.rsplit(".", 1)[0]
        for path in self.shared.all_pages.keys():
            if path.startswith(full_path_without_filetype + "/"):
                self.is_index = True
                break
