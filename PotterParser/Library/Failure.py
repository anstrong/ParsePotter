import json
import os

class NewFailure():
    def __init__(self, errorcode, completed, total):
        self.error = errorcode
        self.completed = completed
        self.total = total

    def __dict__(self):
        return {
            "date": 0,
            "exit code": self.error,
            "completed": self.completed,
            "total": self.total
        }

class QuizRecord():
    def __init__(self, quiz, errorcode, completed, total):
        self.quiz = quiz
        self.error = errorcode
        self.completed = completed
        self.total = total

    def __dict__(self):
        return {
            "title": self.quiz.title,
            "count": 0,
            "failures": []
        }

class Failures():
    def __init__(self):
        self.quizzes = json.load(open(os.path.abspath("FailedQuizzes.json"), "r"))#self.load_history()

    def load_history(self):
        '''with open("Results/FailedQuizList.csv", 'r+') as file:
            quizzes = file.read().splitlines()
            file.close()
        return quizzes'''
        #return json.load(open(os.path.abspath("FailedQuizzes.json"), "r"))

    def get_history(self, quiz):
        for failed_quiz in self.quizzes:
            if failed_quiz.quiz.title is quiz.title:
                return failed_quiz
        return None

    def record_failure(self, quiz, code, completed, total):
        record = self.get_history(quiz)
        if(record == None):
            record = QuizRecord(quiz, code, completed, total)
            self.quizzes.append(record.__dict__())

        failure = NewFailure(code, completed, total)
        record.failures.append(failure)
        record.count += 1

    def update_file(self):
        with open("Results/FailedQuizzes.json", "w+") as file:
            json.dump(self.quizzes, file, indent=4)
            file.close()
