import re

from Library import *
import time
from bs4 import BeautifulSoup, SoupStrainer
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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

def test():
    testAuthor = Author("17578")
    print(testAuthor)

def webTest():
    #myPage2 = Webpage("https://www.qzzr.com/widget/quiz/fi9xdWl6emVzLzQ3NTQ2NT9zdGF0ZVtwX3VdPWh0dHBzJTNBJTJGJTJGd3d3LndpemFyZGluZ3dvcmxkLmNvbSUyRnF1aXolMkZ0aGUtdWx0aW1hdGUtZm9vZC1xdWl6JnN0YXRlW3JdPWh0dHBzJTNBJTJGJTJGd3d3Lmdvb2dsZS5jb20lMkYmc3RhdGVbbl09bm9uZQ/question/fi9zZXNzaW9ucy80ODU4ODY2NjEvMjM2MjcxMQ")
    myPage = Webpage("https://www.wizardingworld.com/quiz/the-ultimate-food-quiz")
    time.sleep(3)
    page = myPage.driver
    button = page.find_element_by_class_name("_1vIqZGTd")#("_23LVVmnZ")#("_3AqE2Mbn")
    print(button)
    myPage.driver.execute_script("arguments[0].setAttribute('style','visibility:visible;');", button)
    #print(myPage.driver.page_source)
    start = button.find_element_by_class_name("quiz-modal")
    myPage.driver.execute_script("arguments[0].setAttribute('style','visibility:visible;');", start)
    #start.switch_to_frame("QUIZ:")
    #element1 = myPage.driver.find_element_by_xpath("/html/body/div/div/div/div/div/div[2]/section/div[2]/div/button")
    #myPage.driver.execute_script("arguments[0].click();", start)

    tags = start.get_attribute('innerHTML')
    soup = BeautifulSoup(tags, "html.parser")
    frame = soup.find_all('iframe')
    txt = str(frame)
    start = txt.find("https:")
    end = txt.find("style") - 2
    link = txt[start:end]
    myPage2 = Webpage(link)
    #myPage2 = Webpage("https://www.qzzr.com/widget/quiz/fi9xdWl6emVzLzQ3NTQ2NT9zdGF0ZVtwX3VdPWh0dHBzJTNBJTJGJTJGd3d3LndpemFyZGluZ3dvcmxkLmNvbSUyRnF1aXolMkZ0aGUtdWx0aW1hdGUtZm9vZC1xdWl6JnN0YXRlW25dPW5vbmU")
    time.sleep(3)
    page2 = myPage2.driver
    #print(page2.page_source)
    #clicker = page2.find_element_by_class_name("QuizCover-start-button")
    #page2.execute_script("arguments[0].setAttribute('style','visibility:visible;');", clicker)
    page2.find_element_by_tag_name("button").click()
    time.sleep(3)
    #print(page2.page_source)
 

    #time.sleep(3)
    options = page2.find_element_by_class_name("QuizQuestion-options-list")
    page2.execute_script("arguments[0].setAttribute('style','visibility:visible;');", options)

    html = BeautifulSoup(page2.page_source,"html.parser")
    answers = html("span",attrs={'class':'QuizQuestionOption-item-label'})
    for opt in answers:
        print(opt.get_text())
    text = html.get_text(", ")

def webTest2(address):
    quiz = Quiz(address)

def webTest3():
    homepage = Webpage("https://www.wizardingworld.com/quiz")
    html = BeautifulSoup(homepage.driver.page_source, "html.parser")
    quizzes = html("a", attrs={'class': ['_2IGobkh6', '_3Wjob5HG']})
    link_item = HTMLItem("href=", "title", 6, 2)
    title_item = HTMLItem("title=", "div", 7, 5)
    quiz_list = []
    for quiz in quizzes:
        str = quiz.prettify()
        address = "https://www.wizardingworld.com" + link_item.extract_from(str)
        title = title_item.extract_from(str)
        quiz_list.append(Quiz(title, address))
        
    print(quiz_list)
    
def webTest4():
    site = Pottermore()
    
    
webTest4()