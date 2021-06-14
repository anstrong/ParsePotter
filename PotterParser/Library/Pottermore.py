import re
import os

from progress.bar import IncrementalBar
from progress.counter import Counter
from bs4 import BeautifulSoup

from .QuizObjects import *
from .Services import *

DB = MongoDatabase()

class Pottermore():
    link_item = HTMLItem("href=", "title", 6, 2)
    title_item = HTMLItem("title=", "div", 7, 5)
    feature_link_item = HTMLItem("href=", "style", 6, 2)
    feature_title_item = HTMLItem("hub_curated_sub_title_", ' ">', 22, 0)

    def __init__(self):
        self.address = "https://www.wizardingworld.com/quiz"
        self.page = Webpage(self.address)
        self.quizzes = []
        self.addresses = []

        #print(DB.quiz_exists("address","https://www.wizardingworld.com/quiz/how-well-know-books-of-hogwarts-library"))

        self.update_list()
        self.parse_quizzes()

        #print(DB.get_unparsed())

        #print(DB.list_duplicates(DB.quizzes(), "address"))
        #print(DB.find_duplicated(DB.quizzes(), "address"))
        DB.remove_all_duplicates(DB.quizzes(), "address")
        #DB.remove_duplicates(DB.quizzes(),"address", "https://www.wizardingworld.com/quiz/weasleys-wizard-wheezes-quiz")
        #print(DB.find_duplicated(DB.quizzes(), "address"))

        self.page.driver.quit()

    def update_list(self):
        #self.spinner = Spinner('Searching for new quizzes ')
        self.counter = Counter('New quizzes found: ')
        self.get_links()
        print('\n')

    def scan_for_new_quiz(self, quiz_chunks):
        for quiz in quiz_chunks:
            #self.spinner.next()
            address = "https://www.wizardingworld.com/quiz/" + quiz.get('href')[6:]
            if (not DB.quiz_exists("address",address)) and (address not in self.addresses):
                self.addresses.append(address)
                self.counter.next()

    def get_links(self):
        height = self.page.driver.execute_script("return document.body.scrollHeight")
        html = BeautifulSoup(self.page.driver.page_source, "html.parser")
        quizzes = html.find_all("a", href=re.compile("/quiz/"))
        self.scan_for_new_quiz(quizzes)

        new_height = self.page.scroll()
        if(new_height != height):
            self.get_links()

    def parse_quizzes(self):
        #print(self.addresses)
        bar = IncrementalBar('Parsing Quizzes', max=len(self.addresses))
        for address in self.addresses:
            try:
                Quiz(address)
                bar.next()
            except:
                print(f'{address} could not be parsed.')
        bar.finish()


