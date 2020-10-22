from .Webpages import *
from .QuizObjects import *
import re
import json

class Pottermore():
    link_item = HTMLItem("href=", "title", 6, 2)
    title_item = HTMLItem("title=", "div", 7, 5)
    feature_link_item = HTMLItem("href=", "style", 6, 2)
    feature_title_item = HTMLItem("hub_curated_sub_title_", ' ">', 22, 0)

    def __init__(self):
        self.address = "https://www.wizardingworld.com/quiz"
        self.page = Webpage(self.address)
        self.quizzes = []
        self.addresses = self.read_links()

        self.update_list()
        self.parse_quizzes()

        self.page.driver.quit()

    def read_links(self):
        with open("Results/QuizList.csv", 'r+') as file:
            links = file.read().splitlines()
            file.close()
        return links

    def write_links(self, links):
        with open("Results/QuizList.csv", 'a+') as file:
            for link in links:
                file.write(link + '\n')
            file.close()

    def update_file(self, new):
        with open("Results/PottermoreQuizzes.json") as file:
            data = json.load(file)
            data.append(new.__dict__())
            file.close()

        with open("Results/PottermoreQuizzes.json", 'w') as f:
            json.dump(data, f, indent=4)

    def add_quiz(self, address):
        try:
            new_quiz = Quiz(address)

        except:
            print(f"{address} couldn't be loaded")
            return

        self.quizzes.append(new_quiz)
        self.update_file(new_quiz)
        with open("Results/ParsedQuizList.csv", 'a+') as file:
            file.write(address[36:]+'\n')
            file.close()

    def update_list(self):
        print("Seaching for new quizzes", end='')
        num_orig = len(self.addresses)
        self.get_links()
        num_new = len(self.addresses)
        self.write_links(self.addresses[num_orig:])
        print(f'{num_new-num_orig} new quizzes found.')

    def scan_for_new_quiz(self, quiz_chunks):
        for quiz in quiz_chunks:
            address = quiz.get('href')[6:]
            if(address not in self.addresses and "chapter" not in address):
                self.addresses.append(address)

    def get_links(self):
        print('.', end='')
        height = self.page.driver.execute_script("return document.body.scrollHeight")
        html = BeautifulSoup(self.page.driver.page_source, "html.parser")
        quizzes = html.find_all("a", href=re.compile("/quiz/"))
        self.scan_for_new_quiz(quizzes)

        new_height = self.page.scroll()
        if(new_height != height):
            self.get_links()

    def parse_quizzes(self):
        with open("Results/QuizList.csv",'r+') as file:
            all_links = file.read().splitlines()
            file.close()

        with open("Results/ParsedQuizList.csv",'r+') as file:
            parsed_links = file.read().splitlines()
            file.close()

        for quiz in all_links:
            if quiz not in parsed_links:
                address = "https://www.wizardingworld.com/quiz/" + quiz
                try:
                    self.add_quiz(address)
                except:
                    break


    def __str__(self):
        result = ""
        for quiz in self.quizzes:
            result+= str(quiz) + '\n'
        return result

    def __dict__(self):
        quiz_list = []
        for quiz in self.quizzes:
            quiz_list.append(dict(quiz))

        return {quiz_list}


