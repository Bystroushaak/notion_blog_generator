

class TransformerBase:
    @classmethod
    def transform(cls, virtual_fs, root, page):
        pass

    @classmethod
    def log_transformer(cls):
        raise NotImplementedError()
