from pymongo import MongoClient
from itertools import chain
from progress.bar import IncrementalBar

class MongoDatabase():
    def __init__(self, user, password):
        MONGODB_URI = f'mongodb+srv://{user}:{password}@quibblecluster.qmsof.mongodb.net/test'
        client = MongoClient(MONGODB_URI)
        QuibbleDB = client['QuibbleDB']
        self.answerDB = QuibbleDB['Answers']
        self.questionDB = QuibbleDB['Questions']
        self.quizDB = QuibbleDB["Quizzes"]

    def quizzes(self):
        return self.quizDB

    def questions(self):
        return self.questionDB

    def answers(self):
        return self.answerDB

    def find_one(self, collection, attr = "", value = ""):
        collection.find_one({attr: value})

    def find_all(self, collection, attr = "", value = ""):
        collection.find({attr: value})

    def find_quiz(self, attr = "", value = ""):
        #print(f'{attr}:{value}')
        return self.find_all(self.quizDB, attr, value)

    def quiz_exists(self, attr="", value=""):
        #quizzes = self.find_quiz(attr, value)
        #print(f'\n{quizzes}')
        #return self.find_one(self.quizDB, attr, value)
        return self.quizDB.find_one({"address": value}) is not None

    def find_question(self, attr = "", value = ""):
        return self.find_one(self.questionDB, attr, value)

    def find_answer(self, attr = "", value = ""):
        return self.find_one(self.answerDB, attr, value)

    def remove(self, collection, id):
        collection.delete_one({"_id": id})

    def remove_quiz(self, id):
        quiz = self.quizDB.find_one({"_id": id})
        for question in quiz["questions"]:
            self.remove_question(question)
        self.remove(self.quizDB, id)

    def remove_question(self, id):
        question = self.questionDB.find_one({"_id": id})
        for answer in question["answers"]:
            self.remove(self.answerDB, answer)
        self.remove(self.questionDB, question)

    def check_duplicates(self, collection, attr = ""): # needs testing
        unique_records = len(collection.distinct(attr))
        total_records = collection.count_documents()
        return unique_records == total_records

    def list_duplicates(self, collection, attr = ""): # inelegant; currently unused
        duplicates = []
        recorded = []
        records = collection.find({})
        for record in records:
            if record not in recorded:
                duplicate_records = collection.find({attr: record[attr]})
                if duplicate_records.count() > 1:
                    duplicate_docs = list(duplicate_records)
                    print(duplicate_docs)
                    for d in range (duplicate_records.count()):
                        id = duplicate_docs[d]['_id']
                        recorded.append(id)
                    duplicates.append(duplicate_docs)
                    #print(duplicate_records.list())
                    #recorded = list(chain.from_iterable(duplicates))
        return duplicates

    def find_duplicated(self, collection, attr=""):
        issue_list = []
        attr = f'${attr}'
        name_cursor = collection.aggregate([
            {'$group': {'_id': attr, 'count': {'$sum': 1}}},
            {'$match': {'count': {'$gt': 1}}}
        ])

        for document in name_cursor:
            name = document['_id']
            issue_list.append(name)
            # print(name)
        return issue_list

    def remove_duplicates(self, collection, attr = "", value = ""):
        duplicates = collection.find({attr: value})
        for i in range(1, duplicates.count()):
            record = duplicates.next()
            if collection is self.quizDB:
                self.remove_quiz(record["_id"])
            elif collection is self.questionDB:
                self.remove_question(record["_id"])
            else:
                self.remove(collection, record["_id"])

    def remove_all_duplicates(self, collection, attr=""):
        duplicated = self.find_duplicated(collection, attr)
        bar = IncrementalBar('Removing Duplicates', max=len(duplicated))
        for record in duplicated:
            self.remove_duplicates(collection, attr, record)
            bar.next()
        bar.finish()

    def get_unparsed(self):
        unparsed = self.quizDB.find({"complete": False})
        record_list = []
        for i in range(1, unparsed.count()):
            record = unparsed.next()
            record_list.append(record["title"])
        return record_list




