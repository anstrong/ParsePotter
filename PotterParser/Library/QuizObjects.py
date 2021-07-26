import json
import os

from progressbar import progressbar
from bs4 import BeautifulSoup

from .WebItems import *
from .Services import *

pause_time = 1
DB = MongoDatabase()

class Quiz():
    template = json.load(open(os.path.abspath("template.json"), "r"))["quiz"]

    def __init__(self, web_driver, address):
        self.address = address
        self.page = web_driver
        self.parse_data()
        self.update()

    def parse_data(self):
        self.load(self.address)
        self.num_questions = self.get_num_questions()
        self.quizID = self.upload()
        self.questions = self.get_questions()

    def load(self, address):
        homepage = self.page.navigate(address)
        #homepage.scroll()
        #homepage.driver.implicitly_wait(2)
        '''#homepage.driver.implicitly_wait(pause_time)
        homepage.scroll()
        homepage.driver.implicitly_wait(pause_time)
        #homepage.driver.find_element_by_tag_name("button").click()
        homepage.driver.find_element_by_class_name("UISubmit-component is-loaded QuizCover-start-button").click()
        homepage.driver.implicitly_wait(pause_time)'''

        inner = homepage.make_visible("quizz-container", "")
        HTML = homepage.driver.page_source
        soup = BeautifulSoup(HTML, "html.parser")
        self.title = soup.find(self.template["title"]["tag"]).getText().replace(self.template["title"]["remove"], "").title()
        backend = soup.find('iframe').get('src')
        if "qzzr" in backend:
            self.page.navigate(backend)#Webpage(backend)
        else:
            #print("Backend Error")
            raise AttributeError("Backend link not a valid quiz address")

    def get_num_questions(self):
        inner = self.page.make_visible(self.template["numberContent"]["class"], "")
        time.sleep(pause_time+1)
        HTML = self.page.driver.page_source
        #print(HTML)

        soup = BeautifulSoup(HTML, "html.parser")
        span = soup.find(self.template["numberContent"]["num_questions"]["tag"], attrs={'class': self.template["numberContent"]["num_questions"]["class"]})
        #span = soup.find("div", "QuizCover-subheading-content-number")
        time.sleep(pause_time+1)
        result = span.get_text()

        num = result.replace(self.template["numberContent"]["num_questions"]["remove"], "")
        return int(num)

    def get_questions(self):
        questions = []
        Question.number = 0
        #for i in range(self.num_questions):
        self.page.driver.find_element_by_tag_name("button").click()
        self.page.driver.implicitly_wait(pause_time)
        for i in progressbar(range(self.num_questions), redirect_stdout=True):
            question = Question(self.page, self.quizID)
            questions.append(question.update())
            self.next()
        return questions

    def next(self):
        try:
            self.page.driver.find_element_by_class_name("QuizQuestion-feedback-header-action").click()
            self.page.driver.implicitly_wait(pause_time)
        except:
            try:
                self.page.driver.find_element_by_class_name("QuizQuestionOption-item-submit-label QuizQuestionOption-item-submit-label-is-active").click()
                self.page.driver.implicitly_wait(pause_time)
            except:
                try:
                    self.page.driver.find_element_by_class_name("UISubmit-component is-loaded QuizCover-start-button").click()
                    self.page.driver.implicitly_wait(pause_time)
                except:
                    self.page.driver.implicitly_wait(.2)

    def upload(self):
        if DB.record_exists(DB.quizzes(),"address",self.address):
            id = DB.find_quiz("address", self.address)['_id']
            return id
        else:
            uploaded_quiz = DB.quizzes().insert_one({
                "label": self.title,
                "address": self.address,
                "questions": [],
                "complete": False,
                "omit": False
            })
            return uploaded_quiz.inserted_id

    def update(self):
        DB.update_record(DB.quizzes(), "_id", self.quizID, "questions", self.questions)
        DB.update_record(DB.quizzes(), "_id", self.quizID, "complete", True)

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
            #print(self.get_question())
            self.questionID = self.upload()
            self.answers = self.get_answers()
            #print(self.answers)
        else:
            print("Question not found")
        #self.page.quit()

    def get_question(self):
        self.page.make_visible(self.template["titleContent"]["class"], "")
        time.sleep(pause_time)
        HTML = BeautifulSoup(self.page.driver.page_source, "html.parser")
        text = HTML.find(self.template["titleContent"]["title"]["tag"], attrs={'class': self.template["titleContent"]["title"]["class"]})
        return text.get_text()

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
                    try:
                        self.page.driver.find_element_by_class_name("QuizQuestionOption-item-content").click()
                    except:
                        self.page.driver.find_element_by_class_name("QuizQuestionOption-image-content").click()
                    time.sleep(pause_time)

        try:
            style_tag = self.page.driver.find_element_by_class_name(answer["option"]["class"])
        except:
            return
        style_attr = style_tag.get_attribute(answer["option"]["attribute"])
        for option in answer["option"]["options"]:
            if style_attr == option["label"]:
                self.answer_style = option["label"]
                style_id = option["id"]

        HTML = BeautifulSoup(self.page.driver.page_source, "html.parser")
        answers = HTML.find_all(answer["label"]["tag"], attrs={'class': answer["label"]["class"]})
        #answers = HTML.find_all("label")
        result = []
        for option in answers:
            answer = Answer(option,self.questionID)
            #print(answer)
            result.append(answer.upload())
        self.answers = result
        return result

    def upload(self):
        if DB.record_exists(DB.questions(),"label",self.question):
            id = DB.find_question("label", self.question)["_id"]
            DB.update_record(DB.questions(), "_id", id, "quiz", self.quizID)
            DB.update_record(DB.questions(), "_id", id, "number", self.num)
            return id
        else:
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
        DB.update_record(DB.questions(), "_id", self.questionID, "type", self.answer_type)
        DB.update_record(DB.questions(), "_id", self.questionID, "style", self.answer_style)
        DB.update_record(DB.questions(), "_id", self.questionID, "answers", self.answers)
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
        if DB.record_exists(DB.answers(), "label", self.label):
            id = DB.find_answer("label", self.label)["_id"]
            DB.update_record(DB.answers(), "_id", id, "correct", self.correct)
            return id
        else:
            uploaded_answer = DB.answers().insert_one({
                "question": self.questionID,
                "label": self.label,
                "correct": self.correct
            })
            return uploaded_answer.inserted_id


    def __repr__(self):
        return self.label


