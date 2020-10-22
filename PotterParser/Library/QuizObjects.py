import os
from .Webpages import *
import json

pause_time = 1

class Quiz():
    template = json.load(open(os.path.abspath("template.json"), "r"))["quiz"]

    def __init__(self, address):
        self.address = address
        self.parse_data()

    def parse_data(self):
        self.page = self.load(self.address)
        self.num_questions = self.get_num_questions()
        self.questions = self.get_questions()

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
        for i in range(0, self.num_questions):
            print(f"\b\b\b\b\b{i+1}/{self.num_questions}")
            self.next()
            question = Question(self.page)
            questions.append(question)

        return questions

    def next(self):
        self.page.driver.find_element_by_tag_name("button").click()
        self.page.driver.implicitly_wait(pause_time)

    def restart(self):
        print(f"Reparsing {self.title}")
        self.__init__(self.title, self.address)

    def __str__(self):
        result = self.title
        for question in self.questions:
            result += "\n\t" + str(question)
        return result
        #return self.title

    def __dict__(self):
        question_list = []
        for question in self.questions:
            question_list.append(question.__dict__())

        return {
            "title": self.title,
            "address": self.address,
            "questions": question_list
        }



class Question():
    number = 0
    template = json.load(open(os.path.abspath("template.json"), "r"))["quiz"]["question"]

    def __init__(self, page = ""):
        Question.number += 1
        self.num = Question.number
        if page != "":
            self.page = page
            self.question = self.get_question()
            self.answers = self.get_answers()

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
                #self.question += option["prompt"]
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
            answer = Answer(option)
            result.append(answer)
            #print(str(answer))
        self.answers = result
        return result

    def get_question(self):
        self.page.make_visible(self.template["titleContent"]["class"], "")
        time.sleep(pause_time)
        HTML = BeautifulSoup(self.page.driver.page_source, "html.parser")
        text = HTML.find(self.template["titleContent"]["title"]["tag"], attrs={'class': self.template["titleContent"]["title"]["class"]})
        return text.get_text()

    def __str__(self):
        result = ""
        result += self.question
        for answer in self.answers:
            result += "\n\t\t" + str(answer)
        return result

    def __dict__(self):
        answer_list = []
        for answer in self.answers:
            answer_list.append(answer.__dict__())

        return {
            "number": self.num,
            "label": self.question,
            "type": self.answer_type,
            "style": self.answer_style,
            "answers": answer_list
        }


class Answer():
    def __init__(self, chunk = ""):
        if chunk != "":
            self.label = chunk.getText()
            self.correct = (chunk.prettify().find("is-incorrect") == -1)
        else:
            print("Answer not found")

    def __str__(self):
        return str(f'{self.label}: {self.correct}')

    def __dict__(self):
        return {
            "label": self.label,
            "correct": self.correct
        }
