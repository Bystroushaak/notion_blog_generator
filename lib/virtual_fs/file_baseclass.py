import os.path


class FileBase:
    def __init__(self):
        self.parent = None
        self.filename = "FileBase"

    def set_parent(self, parent):
        self.parent = parent

    @property
    def is_data(self):
        return False

    @property
    def is_html(self):
        return False

    @property
    def is_directory(self):
        return False

    def get_root_dir(self):
        page = self
        while page.parent:
            page = page.parent

        return page

    def yield_parents(self):
        parent = self.parent
        while parent:
            yield parent
            parent = parent.parent

    @property
    def path(self):
        path = [self.filename]
        parent = self.parent
        while parent:
            path.append(parent.filename)
            parent = parent.parent

        path.reverse()

        if len(path) > 1:
            full_path = os.path.join(*path)
        else:
            full_path = path[0]

        if not full_path.startswith("/"):
            full_path = "/" + full_path

        return full_path

    def save_as(self, file_path):
        raise NotImplementedError()
