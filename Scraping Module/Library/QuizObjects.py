from .WebItems import *
from .Webpages import *

class Quiz():
    backend_link = HTMLItem("https:", "style", 0, 2)

    def __init__(self, title, address):
        self.title = title
        self.address = address
        self.page = self.load_backend(self.address)
        self.num_questions = self.get_num_questions()
        #self.questions = self.get_questions()
        #print(self.questions)

    def load_backend(self, address):
        homepage = Webpage(address)
        homepage.make_visible("_1vIqZGTd", "")
        wrapper = homepage.make_visible("quiz-modal", "")
        HTML = wrapper.get_attribute('innerHTML')
        soup = BeautifulSoup(HTML, "html.parser")
        frame = soup.find_all('iframe')
        txt = str(frame)
        new_address = self.backend_link.extract_from(txt)
        return Webpage(new_address)

    def get_num_questions(self):
        self.page.make_visible("QuizCover-subheading-content", "")
        wrapper = self.page.driver.find_element_by_class_name("QuizCover-subheading-content")
        HTML = wrapper.get_attribute('innerHTML')
        soup = BeautifulSoup(HTML, "html.parser")
        result = soup.get_text()
        try:
            return int(result[:result.find("q") - 1])
        except:
            self.page.driver.refresh()
            print(f"Number of questions not found on {self.title}; reloading")
            self.get_num_questions()


    def get_questions(self):
        questions = []
        for i in range (0, self.num_questions):
            self.next()
            questions.append(Question(self.page))

    def next(self):
        self.page.driver.find_element_by_tag_name("button").click()
        time.sleep(3)

    def __repr__(self):
        return str(f'{self.title} [{self.num_questions} questions]')

class Question():
    number = 0;

    def __init__(self, page):
        Question.number += 1
        self.num = Question.number
        self.page = page
        self.answers = self.get_answers()
        self.question = self.get_question()

    def get_answers(self):
        self.page.make_visible("QuizQuestion-options-list", "")
        first_answer = self.page.driver.find_element_by_class_name("QuizQuestion-options-list")
        first_answer.click()
        time.sleep(3)

        HTML = BeautifulSoup(self.page.driver.page_source, "html.parser")
        answers = HTML("span", attrs={'class': 'QuizQuestionOption-item-label'})
        result = []
        for option in answers:
            result.append(Answer(option))
        return result

    def get_question(self):
        self.page.make_visible("QuizQuestion-options-legend", "")
        HTML = BeautifulSoup(self.page.driver.page_source, "html.parser")
        text = HTML.find(attrs={'class': 'QuizQuestion-info-title'})
        return text.get_text()

    def __repr__(self):
        return self.question

class Answer():
    def __init__(self, chunk):
        print(chunk)
        self.label = self.get_label(chunk)
        self.correct = self.get_correct(chunk)

    def get_label(self, chunk):
        return chunk.get_text()

    def get_correct(self, chunk):
        if chunk.prettify().find("is-incorrect") != -1:
            return False
        else:
            return True

    def __repr__(self):
        return str(f'{self.label}: {self.correct}')
