from urllib.request import Request, urlopen
from bs4 import BeautifulSoup, SoupStrainer
import re, http

hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}

class Webpage():
    global hdr

    def __init__(self, address):
        self.address = address
        try:
            self.html = self.load_page()
            self.text = self.get_text()
        except:
            print("Webpage error: " + str(self))
            raise Exception("Webpage error: " + str(self))

    def load_page(self):
        try:
            url = Request(self.address, headers = hdr)
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

class ListedPage(Webpage):
    def __init__(self, address):
        super().__init__(address)

    def find_all(self, a_str, sub):
        start = 0
        while True:
            start = a_str.find(sub, start)
            if start == -1:
                return
            yield start
            start += len(sub)

    def get_ids(self):
        idIndexes = list(self.find_all(self.text, "id"))

        ids = []
        for num in idIndexes[1:]:
            text = self.text
            ids.append(text[(num+5):(num+(text[num:].find("href"))-3)])

        if len(ids) == 1:
            raise Exception("No IDs found; limit of database has likely been reached")

        return ids


class Quiz():
    def __init__(self, ID):
        self.ID = ID
        try:
            self.page = Webpage(f"https://www.qzzr.com/api/quizzes/{self.ID}")
        except:
            raise Exception(f"{self.page} cannot be loaded")
        else:
            self.title = self.get_title()
            self.author = self.get_author()
            #self.count = self.get_count()
            #self.questions = self.get_questions()

    def get_title(self):
        start = self.page.text.find("title")
        end  = self.page.text.find("description")
        return self.page.text[start + 8: end - 3]

    def get_author(self):
        start = self.page.text.find("author")
        end  = self.page.text.find("questions")
        result = self.page.text[start + 48: end - 4]
        return result#Author(result)

    def get_count(self):
        start = self.page.text.find("count")
        end  = self.page.text.find("slug")
        return int(self.page.text[start + 7: end - 3])

    def get_questions(self):
        qPage = ListedPage(f"https://www.qzzr.com/api/quizzes/{self.ID}/questions/")

        idList = qPage.get_ids()

        questionList = []
        for q in range (self.count-1):
            newQuestion = Question(idList[q])
            questionList.append(newQuestion)

        return questionList

    def __str__(self):
        return str(f'{self.title}, written by {self.author.name}')


class Question():
    def __init__(self, ID):
        self.ID = ID
        try:
            self.page = Webpage(f"https://www.qzzr.com/api/questions/{self.ID}")
            self.answersPage = ListedPage(f"https://www.qzzr.com/api/questions/{self.ID}/answers")
        except:
            raise Exception(f"{self.page} or {self.answersPage} cannot be loaded")
        else:
            self.prompt = self.get_prompt()
            self.options = self.get_options()
            self.order = self.get_order()
            self.correct

    def get_prompt(self):
        start = self.page.text.find("title")
        end  = self.page.text.find("quiz")
        return self.page.text[start + 7: end - 3]

    def get_options(self):
        idList = self.answersPage.get_ids()

        answerList = []
        for a in range (len(idList)-1):
            newAnswer = Answer(idList[a])
            answerList.append(newAnswer)
            if newAnswer.correct:
                self.correct = newAnswer

        return answerList

    def get_order(self):
        start = self.page.text.find("question_order")
        end  = self.page.text.find("random_answers")
        return int(self.page.text[start + 13: end - 2])

    def __str__(self):
        return str(f'{self.prompt}?')

class Answer():
    def __init__(self, ID):
        self.ID = ID
        try:
            self.page = Webpage(f"https://www.qzzr.com/api/answers/{self.ID}")
        except:
            raise Exception(f"{self.page} cannot be loaded")
        else:
            self.value = self.get_value()
            self.correct = self.is_correct()
            self.order = self.get_order()

    def get_value(self):
        start = self.page.text.find("label")
        end  = self.page.text.find("question_id")
        return self.page.text[start + 7: end - 3]

    def is_correct(self):
        start = self.page.text.find("is_correct")
        end  = self.page.text.find("answer_order")
        result = self.page.text[start + 11: end - 2]
        return result == "true"

    def get_order(self):
        start = self.page.text.find("answer_order")
        end  = self.page.text.find("}")
        return int(self.page.text[start + 13: end - 1])

    def __str__(self):
        return str(f'{self.value}: {self.correct}')

class Author():
    def __init__(self, ID):
        self.ID = ID
        try:
            self.page = Webpage(f"https://www.qzzr.com/api/users/{self.ID}")
            self.pubPage = ListedPage(f"https://www.qzzr.com/api/users/{self.ID}/published")
        except:
            raise Exception(f"{self.page} or {self.pubPage} cannot be loaded")
        else:
            self.name = self.get_name()
            self.username = self.get_username()
            #self.quizzes = self.get_quizzes()
            #self.numQuizzes = len(self.quizzes)

    def get_username(self):
        start = self.page.text.find("nickname")
        if(start > 25):
            end  = self.page.text.find("image")
            return self.page.text[start + 11: end - 3]
        else:
            return "None"

    def get_name(self):
        start = self.page.text.find("display_name")
        end  = self.page.text.find("initials")
        return self.page.text[start + 15: end - 3]

    def get_quizzes(self):
        idList = self.pubPage.get_ids()

        quizList = []
        for q in range (len(idList)-1):
            newQuiz = Quiz(idList[q])
            quizList.append(newQuiz)

        return quizList

    def __str__(self):
        return str(f'{self.name} ("{self.nickname}"): {self.numQuizzes} quizzes published')

def download_users():
    path = '/Users/annabelle_strong/Downloads/'
    filename = "Possible Potters.txt"
    f = open(path + filename,"w")

    keywords = ["potter", "wizarding", "rowling"]
    page = 1
    more = True

    while more:
        print(page)
        try:
            current = ListedPage(f"https://www.qzzr.com/api/quizzes/all_published?page={page}")
            quizzes = current.get_ids()
            for quizID in quizzes:
                try:
                    newQuiz = Quiz(quizID)
                except:
                    pass
                else:
                    #if(any(ele in newQuiz.author.lower() for ele in keywords)):
                    #if(any(ele in newQuiz.author.name.lower() for ele in keywords) or any(ele in newQuiz.author.username.lower() for ele in keywords)):
                    f.write(str(newQuiz.author) + "\n")
            page += 1
        except:
            more = False
            break

    f.close()


def find_potters():
    keywords = ['potter', 'wizarding', 'rowling']
    path = '/Users/annabelle_strong/Downloads/'
    filename = "Possible Potters.txt"
    filename2 = "Actually Maybe Potters.txt"
    f = open(path + filename,"r")
    f2 = open(path + filename2, "w")

    idList = f.readlines()
    num = len(idList)
    for i in range(num):
        print(f"{i}/{num}")
        ID = idList[i][1:]
        #print(ID)
        try:
            newAuthor = Author(ID)
        except:
            pass
        else:
            if any(ele in newAuthor.name.lower() for ele in keywords) or any(ele in newAuthor.username.lower() for ele in keywords):
                f2.write(f"{newAuthor.name} ({newAuthor.username}): #{ID}")
                print("!")

    f.close()
    f2.close()

find_potters()
