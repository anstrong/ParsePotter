import re

from progressbar import progressbar
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

    def __init__(self, parse, reparse = False):
        if(parse):
            self.address = "https://www.wizardingworld.com/quiz"
            self.page = Webpage(self.address)
            if reparse:
                unparsed = DB.get_unparsed()
                #print(unparsed)
                self.addresses = list(reversed(unparsed))
            else:
                self.addresses = []
                self.quizzes = []

                self.update_list()

            print(self.addresses)
            self.parse_addresses(self.addresses)
            self.page.quit()

        else:
            print("parsed no quizzes")
            #DB.quizzes().update_many({}, {"$set": {"omit": False}})


    def update_list(self):
        self.counter = Counter('New quizzes found: ')
        self.get_links()
        print('\n')

    def scan_for_new_quiz(self, quiz_chunks):
        for quiz in quiz_chunks:
            address = "https://www.wizardingworld.com/quiz/" + quiz.get('href')[6:]
            if ((not DB.quiz_exists("address",address)) and (address not in self.addresses) and ("chapter" not in address) and not DB.quiz_omitted("address",address)):
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

    def parse_addresses(self, address_list):
        for i in progressbar(range(len(address_list)), redirect_stdout=True):
            address = address_list[i]
            #try:
            Quiz(self.page, address)
            #except:
               # print(f'{address} could not be parsed.')

    def parse_quizzes(self):
        self.parse_addresses(self.addresses)

    def reparse_quizzes(self):
        self.parse_addresses(DB.get_unparsed())



