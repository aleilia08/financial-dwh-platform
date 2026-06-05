from dataclasses import dataclass


@dataclass
class FakeInsertResult:
    inserted_id: str


class FakeCursor:
    def __init__(self, items):
        self.items = list(items)

    def sort(self, field, direction):
        reverse = direction == -1
        self.items.sort(key=lambda item: item.get(field), reverse=reverse)
        return self

    def skip(self, offset):
        self.items = self.items[offset:]
        return self

    def limit(self, limit):
        self.items = self.items[:limit]
        return self

    def __iter__(self):
        return iter(self.items)


class FakeCollection:
    def __init__(
        self,
        *,
        find_one_result=None,
        find_result=None,
        inserted_id="fake-id"
    ):
        self.find_one_result = find_one_result
        self.find_result = list(find_result or [])
        self.inserted_id = inserted_id
        self.inserted_documents = []
        self.queries = []

    def find_one(self, query, projection=None):
        self.queries.append(("find_one", query, projection))
        return self.find_one_result

    def insert_one(self, document):
        self.inserted_documents.append(document.copy())
        return FakeInsertResult(self.inserted_id)

    def find(self, query, projection=None):
        self.queries.append(("find", query, projection))
        return FakeCursor(self.find_result)


class FakeDatabase:
    def __init__(self, collections):
        self.collections = collections

    def __getitem__(self, name):
        return self.collections[name]