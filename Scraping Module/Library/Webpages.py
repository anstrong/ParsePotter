from urllib.request import Request, urlopen
from bs4 import BeautifulSoup, SoupStrainer
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

from .Parseable import Searchable
from .WebItems import *

class Webpage():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)

    def __init__(self, address):
        self.address = address
        print(self.__str__())

        self.driver = Webpage.driver
        self.driver.get(self.address)

        '''try:
            #self.driver.get(self.address)
            self.driver.implicitly_wait(8)
        except:
            print(f"Webpage error: {self.address}")
            raise Exception(f"Webpage error: {self.address}")'''

    def make_visible(self, class_name, wrapper = ""):
        try:
            if wrapper == "":
                wrapper = Webpage.driver
            element = wrapper.find_element_by_class_name(class_name)
            Webpage.driver.execute_script("arguments[0].setAttribute('style','visibility:visible;');", element)
            return element
        except:
            Webpage.driver.refresh()
            print(f"{class_name} not found on {self.address}; reloading")
            self.make_visible(class_name, wrapper)

    def refresh(self):
        self.driver.get(self.address)

    def __str__(self):
        return self.address

