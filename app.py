from flask import Flask, jsonify, redirect
from bson import json_util, objectid
import json
import random
import os

import Services

app = Flask(__name__)
app.config["DEBUG"] = True

DB = Services.MongoDatabase(os.environ.get("MONGO_USER"),os.environ.get("MONGO_PASS"))

if __name__ == '__main__':
    #app.debug = True
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

def clean(data):
    return json.loads(json.dumps(data, sort_keys=True, indent=4, default=json_util.default))

def ID(num):
    return objectid.ObjectId(num)

def get_quiz_with_attr(field, value):
    return DB.find_quiz(field, value)

def unpack_quiz(data):
    quiz = data
    questions = data["questions"]
    quiz['questions'] = unpack_questions(questions)
    return quiz

def unpack_questions(list):
    result = []
    for question in list:
        id = question['$oid']
        question = clean(DB.find_question("_id", ID(id)))
        answers = question['answers']
        question['answers'] = unpack_answers(answers)
        result.append(question)
    return result

def unpack_answers(list):
    result = []
    for answer in list:
        id = answer['$oid']
        answer = clean(DB.find_answer("_id", ID(id)))
        result.append(answer)
    return result

@app.route('/')
@app.route('/index')
def index():
    return "Welcome to the Quibble API!"

@app.route('/quizzes',  methods=['GET'])
@app.route('/quizzes/',  methods=['GET'])
@app.route('/quizzes/all',  methods=['GET'])
def get_all_quizzes():
    data = clean(DB.get_all_json(DB.quizzes()))
   #print(data)
    return {"result":data}

@app.route('/quizzes/id/<string:id>', methods=['GET'])
@app.route('/quizzes/id/<string:id>/', methods=['GET'])
def get_quiz_by_id(id):
    data = clean(DB.find_quiz("_id", ID(id)))
    quiz = clean(unpack_quiz(data))

    if quiz:
        return quiz
    else:
        return "Quiz not found"

@app.route('/quizzes/name/<string:name>', methods=['GET'])
@app.route('/quizzes/name/<string:name>/', methods=['GET'])
def get_quiz_by_name(name):
    address = "https://www.wizardingworld.com/quiz/" + name
    data = clean(DB.find_quiz("address", address))
    quiz = clean(unpack_quiz(data))

    if quiz:
        return quiz
    else:
        return "Quiz not found"

def get_quiz_question(quiz_data, num):
    question_data = quiz_data.get("questions")
    if num:
        if num < len(question_data) and 0 < num:
            try:
                return clean(question_data[num-1])
                #id = str(quiz_data[num-1]['$oid'])
                #question = DB.find_question("_id",ID(id))
                #return clean(question)
            except:
                return "Question not found"
        else:
            return "Question out of bounds"
    else:
        return jsonify(quiz_data)

@app.route('/quizzes/id/<string:id>/questions', methods=['GET'])
@app.route('/quizzes/id/<string:id>/questions/<int:question_num>', methods=['GET'])
def get_quiz_question_by_id(id, question_num = None):
    quiz_data = get_quiz_by_id(ID(id))
    return get_quiz_question(quiz_data, question_num)

@app.route('/quizzes/name/<string:name>/questions', methods=['GET'])
@app.route('/quizzes/name/<string:name>/questions/<int:question_num>', methods=['GET'])
def get_quiz_question_by_name(name, question_num = None):
    address = "https://www.wizardingworld.com/quiz/" + name
    quiz_data = get_quiz_by_name(name)

    return get_quiz_question(quiz_data, question_num)

def generate_rand_quiz_id():
    quizzes = get_all_quizzes()
    index = random.randint(0, len(quizzes)-1)
    quiz = quizzes["result"][index]
    return clean(quiz)["_id"]["$oid"]

@app.route('/random', methods=['GET'])
@app.route('/random/quiz', methods=['GET'])
@app.route('/quizzes/random', methods=['GET'])
def get_random_quiz():
    id = generate_rand_quiz_id()
    quiz = get_quiz_by_id(id)
    if not quiz.get("complete"):
        get_random_quiz()
    else:
        return redirect(f'/quizzes/id/{id}', code=302)

@app.route('/random/question', methods=['GET'])
def get_random_question():
    id = generate_rand_quiz_id()
    quiz = get_quiz_by_id(id)
    index = random.randint(0, len(quiz.get("questions"))-1)
    return redirect(f'/quizzes/id/{id}/questions/{index}', code=302)

@app.route('/addresses/all',  methods=['GET'])
@app.route('/addresses',  methods=['GET'])
@app.route('/addresses/',  methods=['GET'])
def get_addresses():
    addresses = []
    quizzes = DB.get_all(DB.quizzes())
    for quiz in quizzes:
        addresses.append(quiz["address"])
    return jsonify(addresses)

@app.route('/addresses/parsed',  methods=['GET'])
def get_parsed():
    return jsonify(clean(DB.get_record_list(DB.quizzes(), "complete", True, "address")))
