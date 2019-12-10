import os.path

import dhtmlparser

from .postprocessor_base import Postprocessor


class AddBreadcrumb(Postprocessor):
    @classmethod
    def postprocess(cls, dom, page, shared):
        if "/" not in page.path:
            return

        bread_crumbs = []

        path = ""
        dirs = page.path.rsplit("/", 1)[0].split("/")  # just the dirs
        for dirname in dirs:
            full_path = os.path.join(path, dirname + ".html")
            title = shared.all_pages[full_path].title
            path_up = (len(dirs) - len(full_path.split("/"))) * "../" + "index.html"
            bread_crumbs.append([path_up, title])
            path = os.path.join(path, dirname)

        items = ["<a href='{}' class='breadcrumb'>{}</a>".format(*item)
                 for item in bread_crumbs]
        items.append(page.title)

        all_items = " / ".join(items) + "\n\n"
        all_items_tag = dhtmlparser.parseString(all_items)

        dom.find("body")[0].childs.insert(0, all_items_tag)