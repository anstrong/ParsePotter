from urllib.request import Request, urlopen
from bs4 import BeautifulSoup, SoupStrainer
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import time

from .Parseable import Searchable
from .WebItems import *

class Webpage():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)

    def __init__(self, address):
        self.address = address
        print(self.__str__())

        self.driver = Webpage.driver
        self.driver.get(self.address)
        self.driver.implicitly_wait(2)

    def make_visible(self, class_name, wrapper = ""):
        try:
            if wrapper == "":
                wrapper = Webpage.driver
            element = wrapper.find_element_by_class_name(class_name)
            Webpage.driver.execute_script("arguments[0].setAttribute('style','visibility:visible;');", element)
            return element
        except:
            #Webpage.driver.refresh()
            print(f"{class_name} not found on {self.address}")

    def refresh(self):
        self.driver.get(self.address)

    def scroll(self):
        self.driver.find_element_by_tag_name('body').send_keys(Keys.END)
        time.sleep(1)
        self.driver.execute_script("window.scrollBy(0, -500);")
        time.sleep(.5)
        return self.driver.execute_script("return document.body.scrollHeight")

    def __str__(self):
        return self.address

    def __repr__(self):
        return self.address

