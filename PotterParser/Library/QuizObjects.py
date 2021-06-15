import json
import os

from progressbar import progressbar
from bs4 import BeautifulSoup

from .WebItems import *
from .Services import *

pause_time = .5
DB = MongoDatabase()

class Quiz():
    template = json.load(open(os.path.abspath("template.json"), "r"))["quiz"]

    def __init__(self, address):
        self.address = address
        self.parse_data()
        self.update()

    def parse_data(self):
        self.page = self.load(self.address)
        self.num_questions = self.get_num_questions()
        self.quizID = self.upload()
        self.questions = self.get_questions()
        self.page.quit()

    def load(self, address):
        homepage = Webpage(address)
        homepage.driver.find_element_by_tag_name("button").click()
        homepage.driver.implicitly_wait(pause_time)

        inner = homepage.make_visible("quizz-container", "")
        HTML = homepage.driver.page_source
        soup = BeautifulSoup(HTML, "html.parser")
        self.title = soup.find(self.template["title"]["tag"]).getText().replace(self.template["title"]["remove"], "").title()
        backend = soup.find('iframe').get('src')
        if "qzzr" in backend:
            return Webpage(backend)
        else:
            raise AttributeError("Backend link not a valid quiz address")

    def get_num_questions(self):
        time.sleep(pause_time)
        inner = self.page.make_visible(self.template["numberContent"]["class"], "")
        HTML = self.page.driver.page_source

        soup = BeautifulSoup(HTML, "html.parser")
        span = soup.find(self.template["numberContent"]["num_questions"]["tag"], attrs={'class': self.template["numberContent"]["num_questions"]["class"]})
        time.sleep(pause_time)
        result = span.get_text()

        num = result.replace(self.template["numberContent"]["num_questions"]["remove"], "")
        return int(num)

    def get_questions(self):
        questions = []
        Question.number = 0
        for i in range(self.num_questions):#for i in progressbar(range(self.num_questions), redirect_stdout=True):
            self.next()
            question = Question(self.page, self.quizID)
            questions.append(question.update())
        return questions

    def next(self):
        self.page.driver.find_element_by_tag_name("button").click()
        self.page.driver.implicitly_wait(pause_time)

    def upload(self):
        uploaded_quiz = DB.quizzes().insert_one({
            "title": self.title,
            "address": self.address,
            "questions": [],
            "complete": False
        })
        return uploaded_quiz.inserted_id

    def update(self):
        updated_quiz = DB.quizzes().update_one({'_id': self.quizID}, {
            '$set': {"questions": self.questions, "complete": True}
        })

class Question():
    number = 0
    template = json.load(open(os.path.abspath("template.json"), "r"))["quiz"]["question"]

    def __init__(self, page = None, quizID=0):
        Question.number += 1
        self.num = Question.number
        self.quizID = quizID
        if page is not None:
            self.page = page
            self.question = self.get_question()
            self.questionID = self.upload()
            self.answers = self.get_answers()
        else:
            print("Question not found")
        self.page.quit()

    def get_answers(self):
        self.answer_type = "radio"
        self.answer_style = "text"
        style_id = "item"

        self.page.make_visible(self.template["answerList"]["class"], "")
        time.sleep(pause_time)
        self.page.make_visible(self.template["answerList"]["answerContent"]["class"], "")
        time.sleep(pause_time)
        answer = self.template["answerList"]["answerContent"]["answer"]

        type_tag = self.page.driver.find_element_by_class_name(answer["type"]["class"])
        type_attr = type_tag.get_attribute(answer["type"]["attribute"])
        for option in answer["type"]["options"]:
            if type_attr == option["label"]:
                self.answer_type = option["label"]
                for button in option["clickables"]:
                    self.page.driver.find_element_by_tag_name(button).click()
                    time.sleep(pause_time)

        style_tag = self.page.driver.find_element_by_class_name(answer["option"]["class"])
        style_attr = style_tag.get_attribute(answer["option"]["attribute"])
        for option in answer["option"]["options"]:
            if style_attr == option["label"]:
                self.answer_style = option["label"]
                style_id = option["id"]

        HTML = BeautifulSoup(self.page.driver.page_source, "html.parser")
        answers = HTML(answer["label"]["tag"], attrs={'class': answer["label"]["class"]})
        result = []
        for option in answers:
            answer = Answer(option,self.questionID)
            result.append(answer.upload())
        self.answers = result
        return result

    def get_question(self):
        self.page.make_visible(self.template["titleContent"]["class"], "")
        time.sleep(pause_time)
        HTML = BeautifulSoup(self.page.driver.page_source, "html.parser")
        text = HTML.find(self.template["titleContent"]["title"]["tag"], attrs={'class': self.template["titleContent"]["title"]["class"]})
        return text.get_text()

    def upload(self):
        uploaded_question = DB.questions().insert_one({
            "quiz": self.quizID,
            "number": self.num,
            "label": self.question,
            "type": "",
            "style": "",
            "answers": []
        })
        return uploaded_question.inserted_id

    def update(self):
        updated_question = DB.questions().update_one({'_id': self.questionID}, {
            '$set': {"type": self.answer_type, "style": self.answer_style, "answers": self.answers}
        })
        return self.questionID


class Answer():
    def __init__(self, chunk = "", questionID=0):
        self.questionID = questionID
        if chunk != "":
            self.label = chunk.getText()
            self.correct = (chunk.prettify().find("is-incorrect") == -1)
        else:
            print("Answer not found")

    def upload(self):
        uploaded_answer = DB.answers().insert_one({
            "question": self.questionID,
            "label": self.label,
            "correct": self.correct
        })
        return uploaded_answer.inserted_id

