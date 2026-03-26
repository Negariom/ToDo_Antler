class TodoStore:

    
    def __init__(self):
        self._items = {}
        self._next_id = 1

    def add(self, text):
        self._items[self._next_id] = {"text": text, "done": False}
        self._next_id += 1

    def done(self, index):
        key = self._get_key_by_index(index)
        self._items[key]["done"] = True

    def delete(self, index):
        key = self._get_key_by_index(index)
        del self._items[key]

    def showList(self):
        if not self._items:
            print("Brak zadan.")
            return
        for i, item in enumerate(self._items.values(), start=1):
            status = "x" if item["done"] else " "
            print(f"{i}. [{status}] {item['text']}")

    def _get_key_by_index(self, index):
        if index < 1 or index > len(self._items):
            raise ValueError(f"Niepoprawny numer zadania: {index}")
        return list(self._items.keys())[index - 1]

