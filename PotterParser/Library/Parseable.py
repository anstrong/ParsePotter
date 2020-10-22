class Searchable():
    def __init__(self, *args):
        pass

    def parse_data(self, text, item):
        return item.extract_from(text)

    def find_all(self, text, substr):
        start = 0
        while True:
            start = text.find(substr, start)
            if start == -1:
                return
            yield start
            start += len(substr)

    def parse_items(self, text, item):
        keyword = item.start
        itemIndexes = list(self.find_all(text, keyword))

        itemList = []
        for num in itemIndexes:
            subtext = text[num:]
            itemList.append(self.parse_data(subtext, item))

        return itemList
