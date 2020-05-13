from .WebItems import *
from .Webpages import *
from typing import TypeVar

class QuizObject():
    delimiter = ","
    def __init__(self):
        self.has_subitems = False
        self.delimiter = ","
        self.name = ""
        if self.has_subitems:
            self.subitems = self.get_subitems()

    def get_subitems(self):
        pass

    def __str__(self):
        result = self.name
        if self.has_subitems:
            for subitem in self.subitems:
                result += "\n\t" + str(subitem)
        return result

    def __repr__(self):
        content = ""
        for subitem in self.subitems:
            content += repr(subitem) + self.delimiter
        name = self.name.replace(",", "&#44")
        return str(f"{name},{content}")

class ParsedObject(QuizObject):
    def __init__(self, page, name = ""):
        super()
        if isinstance(page, Webpage):
            self.page = page
        else:
            self.page = Webpage(page)

        if name != "":
            self.name = name
        else:
            self.name = self.get_name()

        self.subitems = self.get_subitems()

    def get_subitems(self):
        pass

    def get_name(self):
        pass

    def restart(self):
        print(f"Reparsing {self.name}")
        self.__init__(self.address, self.name)

class ReadObject(QuizObject):
    def __init__(self, content):
        super()
        self.subitems = self.read_data()
        self.subtype = TypeVar('S', Question, Answer)

    def read_data(self):
        content = CSV(self.content).extract()
        self.name = content[0]
        self.address = content[1]
        self.num_questions = int(content[2])
        if self.has_subitems:
            subitems = []
            for i in range(3, 2 * self.num_questions, 2):
                new_subitem = self.subtype(f"{content[i],content[i + 1]}")
                subitems.append(new_subitem)
        return subitems


class ParsedQuiz(ParsedObject):
    backend_link = HTMLItem("https:", "style", 0, 2)
    number_item = HTMLItem(".0.1.$2.$0.$1.2:2.$0.0.0.$1.0", "</span>", 2, 1)

    def __init__(self, title, address, content_str = ""):
        self.title = title
        self.address = address

        self.questions = self.parse_data()

    def parse_data(self):
        self.page = self.load_backend(self.address)
        self.page.driver.implicitly_wait(5)
        self.num_questions = self.get_num_questions()
        self.questions = self.get_questions()

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
            #print(f"\b\b\b\b\b{i+1}/{self.num_questions}")
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