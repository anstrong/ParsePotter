from .Parseable import Searchable

class HTMLItem():
    def __init__(self, key1, key2, buff1, buff2):
        self.start = key1
        self.end = key2
        self.frontBuffer = buff1
        self.backBuffer = buff2

    def extract_from(self, text):
        self.begin = text.find(self.start) + self.frontBuffer
        self.stop = text.find(self.end) - self.backBuffer
        return text[self.begin:self.stop]

class CSVItem():
    def __init__(self, text, delimiter):
        self.delimiter = delimiter
        self.text = text

    def extract_num(self):
        index = 0
        text = self.text
        for i in range (0, self.num-1):
            text = text[text.find(self.delimiter):]
        index = text.find(self.delimiter)
        return text[:index]

class CSV():
    def __init__(self, text):
        self.text = text

    def extract(self, text = "", delimiter = ","):
        if text == "":
            text = self.text

        items = []
        num_items = text.count(delimiter)

        for i in range (0, num_items):
            if(text.find(delimiter) != -1):
                index = text.find(delimiter)
                str = text[:index]
                text = text[index+1:]
            else:
                str = text

            if (str.count(",") > 0):
                str = self.extract(str, ",")
            elif (str.count(";") > 0):
                str = self.extract(str, ";")
            else:
                str = str.replace("&#44", ",")

            items.append(str)

        return items
