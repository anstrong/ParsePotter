from .WebItems import *
from .Webpages import *
from .QuizObjects import *

class Pottermore():
    link_item = HTMLItem("href=", "title", 6, 2)
    title_item = HTMLItem("title=", "div", 7, 5)
    feature_link_item = HTMLItem("href=", "button", 6, 7)
    feature_title_item = HTMLItem("hub_curated_sub_title_", ' ">', 22, 0)

    def __init__(self):
        self.file = open("PottermoreQuizzes.csv", "r");
        self.quizzes = self.read()
        self.file.close()
        print(str(self))

        self.address = "https://www.wizardingworld.com/quiz"
        self.page = Webpage(self.address)

        self.file = open("PottermoreQuizzes.csv", "a+");
        self.get_newest()
        #print(str(self.quizzes))
        #for quiz in self.quizzes:
            #print(str(quiz))
            #self.write(repr(quiz))
        self.file.close()
        Webpage.driver.quit()

    def write(self, str):
        self.file.write(str)

    def read(self):
        quizzes = []
        lines = self.file.readlines()
        for line in lines:
            new_quiz = Quiz("Title", "Address", line)
            quizzes.append(new_quiz)
        return quizzes


    def update(self, iteration):
        HTML = BeautifulSoup(self.page.driver.page_source, "html.parser")
        quiz_chunks = HTML("a", attrs={'class': ['_2IGobkh6', '_3Wjob5HG']})
        for quiz in quiz_chunks:
            str = quiz.prettify()
            address = "https://www.wizardingworld.com" + self.link_item.extract_from(str)
            title = self.title_item.extract_from(str).strip().replace("&amp;", "and")
            if(title.find("Chapter") == -1):
                self.add_quiz(title, address)

        last_height = self.page.driver.execute_script("return document.body.scrollHeight")
        self.page.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(5)
        new_height = self.page.driver.execute_script("return document.body.scrollHeight")
        if(iteration < 3):
            if new_height == last_height:
                self.page.driver.execute_script("window.scrollTo(0, 350);")
                time.sleep(5)
                self.page.driver.execute_script("window.scrollTo(0, 350);")
                time.sleep(10)
                self.update(iteration+1)
            else:
                last_height = new_height
                self.update(iteration+1)
        else:
            print("No new quizzes found.")

    def add_quiz(self, title, address):
        if self.is_new(title):
            try:
                new_quiz = Quiz(title, address)
                print(str(new_quiz))
                self.quizzes.append(new_quiz)
                self.write(repr(new_quiz))
            except:
                try:
                    new_quiz = Quiz(title, address)
                    self.quizzes.append(new_quiz)
                    self.write(repr(new_quiz))
                except:
                    print(f"{title} couldn't be loaded")
                    return

    def get_newest(self):
        HTML = BeautifulSoup(self.page.driver.page_source, "html.parser")
        quiz_chunk = HTML.find("div", attrs={'class': '_3wlPkll7'})
        str = quiz_chunk.prettify()
        address = "https://www.wizardingworld.com" + self.feature_link_item.extract_from(str)
        title = self.feature_title_item.extract_from(str)
        if self.is_new(title):
            new_quiz = Quiz(title, address)
            self.quizzes.append(new_quiz)
            self.write(repr(new_quiz))

        self.update(0)

    def is_new(self, title):
        quizzes = str(self)
        index = quizzes.find(title)
        #print(f"{title}: {index}")
        if index == -1:
            return True
        else:
            return False

    def __str__(self):
        result = ""
        for quiz in self.quizzes:
            result+= str(quiz) + '\n'
        return result


