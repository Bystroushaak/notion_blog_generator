class ResourceRegistry:
    def __init__(self):
        self._id_counter = 0

        self._item_to_id = {}
        self._id_to_item = {}

    def register_item(self, item):
        item_id = self._item_to_id.get(item)
        if item_id:
            return item_id

        item_id = self._inc_id()

        self._item_to_id[item] = item_id
        self._id_to_item[item_id] = item

        return item_id

    def register_item_as_ref_str(self, item):
        id = self.register_item(item)
        return self.as_ref_str(id)

    def item_by_id(self, id):
        return self._id_to_item.get(id)

    def id_by_item(self, item):
        return self._item_to_id.get(item)

    def item_by_ref_str(self, ref_str):
        id = self.parse_ref_str(ref_str)
        return self.item_by_id(id)

    @staticmethod
    def as_ref_str(id):
        return "resource:%d" % id

    @staticmethod
    def is_ref_str(ref_str):
        return ref_str.startswith("resource:")

    @staticmethod
    def parse_ref_str(ref_str):
        return int(ref_str.split(":")[-1])

    def _inc_id(self):
        id = self._id_counter
        self._id_counter += 1
        return id
