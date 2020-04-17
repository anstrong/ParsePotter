from .WebItems import *
from .Webpages import *
from .QuizObjects import *

class Pottermore():
    link_item = HTMLItem("href=", "title", 6, 2)
    title_item = HTMLItem("title=", "div", 7, 5)
    feature_link_item = HTMLItem("href=", "button", 6, 7)
    feature_title_item = HTMLItem("hub_curated_sub_title_", ' ">', 22, 0)

    def __init__(self):
        self.address = "https://www.wizardingworld.com/quiz"
        self.page = Webpage(self.address)
        self.quizzes = {} #self.read
        self.update()
        print(self.quizzes)

    def write(self):
        pass

    def read(self):
        pass

    def update(self):
        self.get_newest()

        HTML = BeautifulSoup(self.page.driver.page_source, "html.parser")
        quiz_chunks = HTML("a", attrs={'class': ['_2IGobkh6', '_3Wjob5HG']})

        for quiz in quiz_chunks:
            str = quiz.prettify()
            address = "https://www.wizardingworld.com" + self.link_item.extract_from(str)
            title = self.title_item.extract_from(str)
            if self.is_new(title):
                self.quizzes[title] = Quiz(title, address)
                #self.write()

    def get_newest(self):
        HTML = BeautifulSoup(self.page.driver.page_source, "html.parser")
        quiz_chunk = HTML.find("div", attrs={'class': '_3wlPkll7'})
        str = quiz_chunk.prettify()
        address = "https://www.wizardingworld.com" + self.feature_link_item.extract_from(str)
        title = self.feature_title_item.extract_from(str)
        if self.is_new(title):
            self.quizzes[title] = Quiz(title, address)
            # self.write()

    def is_new(self, title):
        quiz = self.quizzes.get(title, -1)
        if quiz == -1:
            return True
        else:
            return False



