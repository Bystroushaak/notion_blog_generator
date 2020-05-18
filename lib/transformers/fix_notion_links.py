from .postprocessor_base import Postprocessor


class FixNotionLinks(Postprocessor):
    @classmethod
    def postprocess(cls, dom, page, shared):
        for a in dom.find("a"):
            link_content = a.getContent().strip()
            if link_content not in shared.title_map:
                continue

            if not a.params.get("href", "").startswith("https://www.notion.so"):
                continue

            path = shared.title_map[link_content].path
            path = path.replace(" ", "%20")
            path = (path.count("/") * "../") + path

            a.params["href"] = path
