from .WebItems import *
from .Webpages import *

class Quiz():
    backend_link = HTMLItem("https:", "style", 0, 2)
    number_item = HTMLItem(".0.1.$2.$0.$1.2:2.$0.0.0.$1.0", "</span>", 2, 1)

    def __init__(self, title, address, content_str = ""):
        self.title = title
        self.address = address

        if content_str == "":
            self.parse_data()
        else:
            self.questions = self.read_data(content_str)

    def parse_data(self):
        self.page = self.load_backend(self.address)
        self.page.driver.implicitly_wait(5)
        self.num_questions = self.get_num_questions()
        self.questions = self.get_questions()

    def read_data(self, content_str):
        content = CSV(content_str).extract()
        self.title = content[0]
        self.address = content[1]
        self.num_questions = int(content[2])
        questions = []
        for i in range(3, 2*self.num_questions, 2):
            new_question = Question()
            new_question.read_content([content[i], content[i+1]])
            questions.append(new_question)
        return questions

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
        time.sleep(5)
        inner = self.page.make_visible("Quiz-content-inner", "")
        HTML = self.page.driver.page_source

        soup = BeautifulSoup(HTML, "html.parser")
        span = soup.find("span", attrs={'class': 'translate-component'})
        result = span.get_text()

        try:
            return int(result[:result.find("q") - 1])
        except:
            self.page.refresh()
            print(f"Number of questions not found on {self.title}; reloading")
            print("PAGE CONTENT:" + span.prettify())
            self.get_num_questions()

    def get_questions(self):
        questions = []
        for i in range(0, self.num_questions):
            print(f"\b\b\b\b\b{i+1}/{self.num_questions}")
            self.next()
            question = Question(self.page)
            questions.append(question)

        return questions

    def next(self):
        self.page.driver.find_element_by_tag_name("button").click()
        self.page.driver.implicitly_wait(3)

    def restart(self):
        print(f"Reparsing {self.title}")
        self.__init__(self.title, self.address)

    def __str__(self):
        result = self.title
        for question in self.questions:
            result += "\n\t" + str(question)
        return result
        #return self.title

    def __repr__(self):
        content = ""
        for question in self.questions:
            content += repr(question) + ","
        title = self.title.replace(",", "&#44")
        #content.replace(",", "&#44")
        return str(f"{title},{self.address},{self.num_questions},{content}\n")

class Question():
    number = 0

    def __init__(self, page = ""):
        Question.number += 1
        self.num = Question.number
        if page != "":
            self.page = page
            self.question = self.get_question()
            self.answers = self.get_answers()

    def get_answers(self):
        self.page.make_visible("QuizQuestion-options-list", "")
        time.sleep(2)
        self.page.make_visible("QuizQuestion-options", "")
        time.sleep(2)

        select_tag = self.page.driver.find_element_by_class_name("QuizQuestionOption-input")
        select_type = select_tag.get_attribute("type")
        if select_type == "checkbox":
            self.page.driver.find_element_by_tag_name("label").click()
            time.sleep(3)
            self.page.driver.find_element_by_tag_name("button").click()
            self.question = f"{self.question} (Select all that apply)"
            time.sleep(3)
        elif select_type == "radio":
            self.page.driver.find_element_by_tag_name("label").click()
            time.sleep(3)

        option_tag = self.page.driver.find_element_by_class_name("QuizQuestion-options")
        tag_classes = option_tag.get_attribute("class")
        tag_classes = tag_classes[tag_classes.find("-") + 8:]
        option_type = tag_classes[tag_classes.find("has-")+4:tag_classes.find("-options")]
        if option_type == "text":
            label_id = "item"
        elif option_type == "image":
            label_id = "image"

        HTML = BeautifulSoup(self.page.driver.page_source, "html.parser")
        answers = HTML("span", attrs={'class': f'QuizQuestionOption-{label_id}-label'})
        result = []
        for option in answers:
            result.append(Answer(option))
        return result

    def get_question(self):
        self.page.make_visible("QuizQuestion-info", "")
        time.sleep(2)
        HTML = BeautifulSoup(self.page.driver.page_source, "html.parser")
        text = HTML.find("h2", attrs={'class': 'QuizQuestion-info-title'})
        return text.get_text()

    def read_content(self, list):
        self.question = str(list[0])
        self.answers = []
        for answer in list[1]:
            new_answer = Answer()
            new_answer.read_content(answer)
            self.answers.append(new_answer)


    def __str__(self):
        result = ""
        result += self.question
        for answer in self.answers:
            result += "\n\t\t" + str(answer)
        return result

    def __repr__(self):
        content = ""
        for answer in self.answers:
            content += repr(answer) + ";"
        question = self.question.replace(",", "&#44")
        #content.replace(",", "&#44")
        return(f"{question},{content}")


class Answer():
    def __init__(self, chunk = ""):
        if chunk != "":
            self.label = self.get_label(chunk)
            self.correct = self.get_correct(chunk)

    def read_content(self, str):
        self.label = str[:str.find("(")]
        correct = str[str.find("(")+1:str.find(")")]
        if correct == "True":
            self.correct = True
        else:
            self.correct = False

    def get_label(self, chunk):
        return chunk.get_text()

    def get_correct(self, chunk):
        if chunk.prettify().find("is-incorrect") != -1:
            return False
        else:
            return True

    def __str__(self):
        return str(f'{self.label}: {self.correct}')

    def __repr__(self):
        label = self.label.replace(",", "&#44")
        return(f"{label}({self.correct})")
