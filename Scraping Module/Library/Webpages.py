from urllib.request import Request, urlopen
from bs4 import BeautifulSoup, SoupStrainer
from selenium import webdriver
import time

from .Parseable import Searchable
from .WebItems import *

class Webpage():
    hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
           'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
           'Accept-Encoding': 'none',
           'Accept-Language': 'en-US,en;q=0.8',
           'Connection': 'keep-alive'}

    def __init__(self, address):
        self.address = address
        self.driver = webdriver.Chrome()
        try:
            self.driver.get(self.address)
            time.sleep(3)
        except:
            print(f"Webpage error: {self.address}")
            raise Exception(f"Webpage error: {self.address}")

    def make_visible(self, class_name, wrapper):
        try:
            if wrapper == "":
                wrapper = self.driver
            element = wrapper.find_element_by_class_name(class_name)
            self.driver.execute_script("arguments[0].setAttribute('style','visibility:visible;');", element)
            return element
        except:
            self.driver.refresh()
            print(f"{class_name} not found on {self.address}; reloading")
            self.make_visible(class_name, wrapper)

    def __str__(self):
        return self.address

class ListedPage(Webpage, Searchable):
    def __init__(self, root, subdir):
        super().__init__(str(f"{root}/{subdir}"))

    def get_ids(self):
        idString = HTMLItem('"id"', "href", 6, 3)
        return self.parse_items(self.text, idString)

class WebObject(Searchable):
    fullyParse = True
    subdirectory = ""

    def __init__(self, ID, connector = False, root = "https://www.qzzr.com/api"):
        self.ID = ID
        self.address = str(f"{root}/{self.subdirectory}/{self.ID}")
        try:
            self.page = Webpage(self.address)
        except:
            raise Exception(str(f"{self.address} cannot be loaded"))
        else:
            self.load_data()

    def load_data(self):
        pass

    def find_attribute(self, item):
        TOLERANCE = 30
        attribute = self.parse_data(self.page.text, item)
        if len(attribute) > TOLERANCE:
            return "None"
        else:
            return attribute

    def get_subitems(self, subdir, itemType, connector = False):
        itemPage = ListedPage(self.address, subdir)
        idList = itemPage.get_ids()

        itemList = []
        for itemID in idList:
            if connector is False:
                newItem = itemType(itemID)
            else:
                newItem = itemType(itemID, connector)
            itemList.append(newItem)

        print(f"{newItem.ID}: {itemList}")
        return itemList

    def __repr__(self):
        return str(self.address)
