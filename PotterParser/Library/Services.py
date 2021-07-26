import os

from pymongo import MongoClient
from itertools import chain
from progress.bar import IncrementalBar
from bson import objectid

class MongoDatabase():
    def __init__(self):
        MONGODB_URI = f'mongodb+srv://{os.environ.get("MONGO_USER")}:{os.environ.get("MONGO_PASS")}@quibblecluster.qmsof.mongodb.net/test'
        client = MongoClient(MONGODB_URI)
        QuibbleDB = client['QuibbleDB']
        self.answerDB = QuibbleDB['Answers']
        self.questionDB = QuibbleDB['Questions']
        self.quizDB = QuibbleDB["Quizzes"]

    ## Collection getters
    def quizzes(self):
        return self.quizDB

    def questions(self):
        return self.questionDB

    def answers(self):
        return self.answerDB

    ## Record getters
    def get_all(self, collection):
        return collection.find({})

    def get_all_json(self, collection):
        records = self.get_all(collection)
        record_list = []
        for i in range(0, records.count()):
            record = records.next()
            record_list.append(record)
        return record_list

    def get_record_list(self, collection, attr="_id", value="", format="_id"):
        records = collection.find({attr: value})
        record_list = []
        for i in range(0, records.count()):
            record = records.next()
            record_list.append(record[format])
        return record_list

    def get_all_unparsed(self):
        return self.get_record_list(self.quizDB, "complete", False, "address")

    def get_unparsed(self):
        records = self.quizzes().find({"complete": False, "omit": False})
        record_list = []
        for i in range(0, records.count()):
            record = records.next()
            record_list.append(record["address"])
        return record_list

    def get_attr(self, collection, search_attr="label", value = "", target_attr="_id"):
        return collection.find_one({search_attr: value})[target_attr]

    ##  Pre-Checks
    def record_exists(self, collection, attr="_id", value=""):
        return self.find_one(collection, attr, value) is not None

    def quiz_exists(self, attr="_id", value=""):
        return self.record_exists(self.quizDB, attr, value)

    def quiz_omitted(self, attr="_id", value=""):
        return self.find_quiz(attr, value)["omit"]


    ## Record Finders
    def find_one(self, collection, attr = "_id", value = ""):
        return collection.find_one({attr: value})

    def find_all(self, collection, attr = "_id", value = ""):
        return collection.find({attr: value})

    def find_quiz(self, attr = "_id", value = ""):
        return self.find_one(self.quizDB, attr, value)

    def find_question(self, attr = "_id", value = ""):
        return self.find_one(self.questionDB, attr, value)

    def find_answer(self, attr = "_id", value = ""):
        return self.find_one(self.answerDB, attr, value)

    ## Removers
    def remove(self, collection, id):
        collection.delete_one({"_id": id})

    def remove_question(self, id):
        answers = self.get_attr(self.questionDB, "_id", id, "answers")
        for answer in answers:
            self.remove(self.answerDB, answer)
        self.remove(self.questionDB, id)

    def remove_quiz(self, id):
        questions = self.get_attr(self.quizDB, "_id", id, "questions")
        for question in questions:
            self.remove_question(question)
        self.remove(self.quizDB, id)

    def remove_quizzes(self, quiz_list):
        bar = IncrementalBar('Removing Quizzes', max=len(quiz_list))
        for quiz in quiz_list:
            self.remove_quiz(quiz)
            bar.next()
        bar.finish()

    def empty_collection(self, collection, record_type):
        records = self.get_all(collection)
        bar = IncrementalBar(f'Removing {record_type}', max=records.count())
        for i in range(records.count()):
            record = records.next()
            self.remove(collection, record["_id"])
            bar.next()
        bar.finish()

    def remove_all(self):
        self.empty_collection(self.answerDB,"Answers")
        self.empty_collection(self.questionDB,"Questions")
        self.empty_collection(self.quizDB,"Quizzes")

    ## Duplication validators
    def has_duplicates(self, collection, attr = "label"):
        return len(self.find_duplicated(collection,attr)) is not 0

    def find_duplicated(self, collection, attr="label"):
        issue_list = []
        attr = f'${attr}'
        name_cursor = collection.aggregate([
            {'$group': {'_id': attr, 'count': {'$sum': 1}}},
            {'$match': {'count': {'$gt': 1}}}
        ])
        for document in name_cursor:
            name = document['_id']
            issue_list.append(name)
        return issue_list

    def remove_duplicates(self, collection, attr = "label", value = ""):
        duplicates = self.find_all(collection, attr, value)
        for i in range(1, duplicates.count()):
            record = duplicates.next()
            if collection is self.quizDB:
                self.remove_quiz(record["_id"])
            elif collection is self.questionDB:
                self.remove_question(record["_id"])
            else:
                self.remove(collection, record["_id"])

    def remove_all_duplicates(self, collection, attr="label"):
        duplicated = self.find_duplicated(collection, attr)
        bar = IncrementalBar('Removing Duplicates', max=len(duplicated))
        for record in duplicated:
            self.remove_duplicates(collection, attr, record)
            bar.next()
        bar.finish()

    ## Integrity validators
    def validate_children(self, record, child_collection, list_name):
        issue_list = []
        for child in record[list_name]:
            if not self.record_exists(child_collection, "_id", child):
                issue_list.append(child)
        return issue_list

    def validate_parent(self, record, parent_collection, attr_name):
        issue_list = []
        if not self.record_exists(parent_collection, "_id", record[attr_name]):
            issue_list.append(record[attr_name])
        return issue_list

    def validate_links(self, collection, collection_name):
        issue_list = []
        records = self.get_all(collection)
        bar = IncrementalBar(f'Validating {collection_name}', max=records.count())
        for i in range(records.count()):
            record = records.next()
            if (collection is self.quizDB) and record["complete"]:
                broken_c_links = self.validate_children(record, self.questionDB, "questions")
                if len(broken_c_links) is not 0:
                    issue_list.append(record["_id"])
            elif collection is self.questionDB:
                broken_c_links = self.validate_children(record, self.answerDB, "answers")
                broken_p_links = self.validate_parent(record, self.quizDB, "quiz")
                if (len(broken_c_links) is not 0) or (len(broken_p_links) is not 0):
                    issue_list.append(record["_id"])
            elif collection is self.answerDB:
                broken_p_links = self.validate_parent(record, self.questionDB, "question")
                if len(broken_p_links) is not 0:
                    issue_list.append(record["_id"])
            bar.next()
        bar.finish()
        return issue_list#list(chain(*issue_list))

    def validate_answers(self):
        return self.validate_links(self.answerDB, "Answers")

    def validate_questions(self):
        return self.validate_links(self.questionDB, "Questions")

    def validate_quizzes(self):
        return self.validate_links(self.quizDB, "Quizzes")

    def validate_all(self):
        issue_list = []
        issue_list.append(self.validate_answers())
        issue_list.append(self.validate_questions())
        issue_list.append(self.validate_quizzes())
        return issue_list

    ## Updaters
    def rename_field(self, collection, current__name, new_name):
        collection.update_many({}, {"$rename": {current__name: new_name}})

    def update_record(self, collection, search_attr, search_value, update_attr, update_value):
        collection.update_one({search_attr: search_value}, {
            '$set': {update_attr: update_value}
        })

















