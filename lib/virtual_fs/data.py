import os.path

from lib.virtual_fs.file_baseclass import FileBase


class Data(FileBase):
    def __init__(self, original_path, content):
        super().__init__()

        self.filename = os.path.basename(original_path)
        self.original_path = original_path
        self.content = content

    @property
    def is_data(self):
        return True

    def save_as(self, file_path):
        with open(file_path, "wb") as f:
            f.write(self.content)
