from urllib.request import Request, urlopen
from bs4 import BeautifulSoup, SoupStrainer

class HTMLItem():
    def __init__(self, key1="", key2="", buff1, buff2):
        self.start = key1
        self.end = key2
        self.frontBuffer = buff1
        self.backBuffer = buff2

    def extract_from(self, text):
        self.begin = text.find(self.start) + self.frontBuffer
        self.end = text.find(self.end) - self.backBuffer
        return text[self.begin:self.end]

class Parseable():
    def parse_data(self, text, item):
        return item.extract_from(text)

    def find_all(text, substr):
        start = 0
        while True:
            start = text.find(substr, start)
            if start == -1:
                return
            yield start
            start += len(substr)

    def parse_items(text, item):
        keyword = item.start
        itemIndexes = list(find_all(text, keyword))

        itemList = []
        for num in itemIndexes[]:
            subtext = text[num - len(keyword):]
            itemList.append(parse_data(subtext, item))

        return itemList


class Webpage():
    cls.hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
           'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
           'Accept-Encoding': 'none',
           'Accept-Language': 'en-US,en;q=0.8',
           'Connection': 'keep-alive'}

    def __init__(self, address):
        self.address = address
        try:
            self.html = self.load_page()
            self.text = self.get_text()
        except:
            print(f"Webpage error: {self.address}")
            raise Exception(f"Webpage error: {self.address}")

    def load_page(self):
        try:
            url = Request(self.address, headers = cls.hdr)
            return urlopen(url).read()
        except:
            raise Exception("Page cannot be loaded")

    def get_text(self):
        try:
            soup = BeautifulSoup(self.html, "html.parser")
            return soup.get_text()
        except:
            raise Exception("Text cannot be loaded")

    def __str__(self):
        return str(f'{self.address}{self.code}')

class ListedPage(Webpage,Parseable):
    def __init__(self, root, subdir):
        super().__init__(root, subdir)

    def get_ids(self):
        idString = HTMLItem("id", "href", 5, 3)
        return parse_items(idString)

class WebObject(Parseable):
    fullyParse = False

    def __init__(self, ID, root = "https://www.qzzr.com/api", subdir):
        self.ID = ID
        self.address = (f"{root}/{subdir}/{self.ID}")
        try:
            self.page = Webpage(address)
        except:
            raise Exception(f"{self.address} cannot be loaded")
        else:
            self.load_data()

    def load_data(self):
        pass

    def find_attribute(self, item):
        TOLERANCE = 30
        attribute = parse_data(self.page.text, item)
        if len(attribute) > TOLERANCE:
            return "None"
        else:
            return attribute

    def get_subitems(self, subdir, itemType, connector = False):
        itemPage = ListedPage(f"{self.address}/{subdir}")
        idList = itemPage.get_ids()

        itemList = []
        for i in range(len(idList)-1):
            if connector is False:
                newItem = itemType(idList[a])
            else:
                newItem = itemType(idList[a], connector)
            ItemList.append(newItem)

        return ItemList

    def __str__(self):
        return str(self.address)

class Author(WebObject):
    nameItem = HTMLItem("nickname", "image", 11, 3)
    usernameItem = HTMLItem("display_name", "initials", 15, 3)

    def __init__(self, ID):
        super().__init__(ID, subdir = "users")

    def load_data(self):
        self.name = self.find_attribute(nameItem)
        self.username = self.find_attribute(usernameItem)
        if fullyParse:
            self.quizzes = self.get_subitems("published", Quiz, self)
            self.numQuizzes = len(self.quizzes)

    def __str__(self):
        return str(f'{self.name} ("{self.nickname}"): {self.numQuizzes}')

class Quiz(WebObject):
    titleItem = HTMLItem("title", "description", 8, 3)
    authorItem = HTMLItem("author", "questions", 48, 4)
    countItem = HTMLItem("count", "slug", 7, 3)

    def __init__(self, ID, knownAuthor = False):
        super().__init__(ID, subdir = "quizzes")

    def load_data(self):
        self.title = self.find_attribute(titleItem)
        self.author = self.find_attribute(authorItem) if knownAuthor is False else knownAuthor
        self.count = self.find_attribute(countItem)
        if fullyParse:
            self.questions = self.get_subitems("questions", Question)

    def __str__(self):
        return str(f'{self.title}, written by {self.author.name} [{self.count} questions]')

class Question(WebObject):
    promptItem = HTMLItem("title", "quiz", 7, 3)
    orderItem = HTMLItem("question_order", "random_answers", 13, 2)

    def __init__(self, ID):
        super().__init__(ID, subdir = "questions")

    def load_data(self):
        self.prompt = self.find_attribute(promptItem)
        self.order = self.find_attribute(orderItem)
        if fullyParse:
            self.options = self.get_subitems("answers", Answer)
            self.correct = self.get_correct()

    def get_correct(self):
        for answer in self.options:
            if answer.correct is True:
                self.correct = answer

    def __str__(self):
        return str(f'{self.prompt}?')

class Answer(WebObject):
    valueItem = HTMLItem("label", "question_id", 7, 3)
    correctItem = HTMLItem("is_correct", "answer_order", 11, 2)
    orderItem = HTMLItem("answer_order", "}", 13, 1)

    def __init__(self, ID):
        super().__init__(ID, subdir = "answers")

    def load_data(self):
        self.value = self.find_attribute(valueItem)
        self.correct = True if self.find_attribute(correctItem) == "true" else False
        self.order = self.find_attribute(orderItem)

    def __str__(self):
        return str(f'{self.value}: {self.correct}')
