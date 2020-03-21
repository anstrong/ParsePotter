import re

from Library import *

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
    myPage = Webpage("https://www.qzzr.com/api/users/17578")
    print(myPage.get_text())

test()
