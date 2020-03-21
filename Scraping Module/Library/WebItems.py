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
