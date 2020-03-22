from .WebItems import *
from .Webpages import *

class Author(WebObject):
    nameItem = HTMLItem("nickname", "image", 11, 3)
    usernameItem = HTMLItem("display_name", "initials", 15, 3)

    subdirectory = "users"
    def __init__(self, ID):
        super().__init__(ID)

    def load_data(self):
        self.name = self.find_attribute(self.nameItem)
        self.username = self.find_attribute(self.usernameItem)
        if self.fullyParse:
            self.quizzes = self.get_subitems("published", Quiz, self)
            self.numQuizzes = len(self.quizzes)
        else:
            self.numQuizzes = -1

    def __repr__(self):
        return str(f'{self.name} ("{self.username}"): {self.numQuizzes}')

class Quiz(WebObject):
    titleItem = HTMLItem("title", "description", 8, 3)
    authorItem = HTMLItem("author", "questions", 48, 4)
    countItem = HTMLItem("count", "slug", 7, 3)

    subdirectory = "quizzes"
    def __init__(self, ID, knownAuthor = False):
        self.knownAuthor = knownAuthor
        super().__init__(ID, knownAuthor)

    def load_data(self):
        self.title = self.find_attribute(self.titleItem)
        self.authorID = self.find_attribute(self.authorItem)
        self.author = Author(self.authorID) if self.knownAuthor is False else self.knownAuthor
        self.count = self.find_attribute(self.countItem)
        if self.fullyParse:
            self.questions = self.get_subitems("questions", Question)

    def __repr__(self):
        return str(f'{self.title}, written by {self.author.name} [{self.count} questions]')

class Question(WebObject):
    promptItem = HTMLItem("title", "quiz", 7, 3)
    orderItem = HTMLItem("question_order", "random_answers", 13, 2)

    subdirectory = "questions"
    def __repr__(self, ID):
        super().__init__(ID)

    def load_data(self):
        self.prompt = self.find_attribute(self.promptItem)
        self.order = self.find_attribute(self.orderItem)
        if self.fullyParse:
            self.options = self.get_subitems("answers", Answer)
            self.correct = self.get_correct()

    def get_correct(self):
        for answer in self.options:
            if answer.correct is True:
                self.correct = answer

    def __repr__(self):
        return str(f'{self.prompt}?')

class Answer(WebObject):
    valueItem = HTMLItem("label", "question_id", 8, 3)
    correctItem = HTMLItem("is_correct", "answer_order", 12, 2)
    orderItem = HTMLItem("answer_order", "}", 13, 1)

    subdirectory = "answers"
    def __init__(self, ID):
        super().__init__(ID)

    def load_data(self):
        self.value = self.find_attribute(self.valueItem)
        self.correct = True if self.find_attribute(self.correctItem) == "true" else False
        self.order = self.find_attribute(self.orderItem)

    def __repr__(self):
        return str(f'{self.value}: {self.correct}')
