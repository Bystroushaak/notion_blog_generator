import os.path

from lib.settings import settings

from .preprocessor_base import PreprocessorBase


class GenerateIndexesForDirectories(PreprocessorBase):
    @classmethod
    def preprocess(cls, virtual_fs, root):
        settings.logger.info("Generating indexes for directories..")

        for dir in root.walk_dirs():
            dirname = os.path.basename(dir.path).strip()

            if not dir.parent:
                continue

            for file in dir.parent.files:
                filename = os.path.basename(file.filename)
                if "." in filename:
                    filename = filename.rsplit(".", 1)[0].strip()

                if dirname == filename:
                    index = file.create_copy()
                    index.filename = "index.html"

                    dir.files.append(index)
                    index.parent = dir
