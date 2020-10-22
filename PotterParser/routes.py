import json
import random
from PotterParser import app
from flask import jsonify, request

def get_quiz_with_attr(field, value):
    results = []
    with open("Results/PottermoreQuizzes.json") as file:
        quizzes = json.load(file)
        file.close()

    if(value != '*'):
        for quiz in quizzes:
            if quiz[field] == value:
                results.append(quiz)
    else:
        results = quizzes

    return results

@app.route('/')
@app.route('/index')
def index():
    return "Welcome to the Quibble API!"

def get_json_data():
    with open("Results/PottermoreQuizzes.json") as file:
        data = json.load(file)
        file.close()
    return data

@app.route('/quizzes',  methods=['GET'])
@app.route('/quizzes/',  methods=['GET'])
@app.route('/quizzes/all',  methods=['GET'])
def get_all_quizzes():
    data = get_json_data()
    return json.dumps(data)

@app.route('/quizzes/<string:id>', methods=['GET'])
@app.route('/quizzes/<string:id>/<int:question>', methods=['GET'])
def get_quiz_question(id, question = 0):
    if '-' in id:
        quiz = get_quiz_addr(id)
    else:
        quiz = get_quiz_title(id)

    if question:
        try:
            return jsonify(quiz['questions'][question])
        except:
            return "Question index out of bounds"
    else:
        return jsonify(quiz)


def get_quiz_addr(address):
    if "wizardingworld.com" not in address:
        address = "https://www.wizardingworld.com/quiz/" + address

    return get_quiz_with_attr('address', address)[0]

def get_quiz_title(title):
    return get_quiz_with_attr('title', title)[0]

@app.route('/random', methods=['GET'])
@app.route('/random/quiz', methods=['GET'])
@app.route('/quizzes/random', methods=['GET'])
def get_random_quiz():
    quizzes = get_json_data()
    index = random.randint(0, len(quizzes)-1)
    return json.dumps(quizzes[index])

@app.route('/random/question', methods=['GET'])
def get_random_question():
    quizzes = get_json_data()
    quiz_index = random.randint(0, len(quizzes)-1)
    quiz = quizzes[quiz_index]
    question_index = random.randint(0, len(quiz["questions"])-1)
    return json.dumps(quiz["questions"][question_index])

@app.route('/addresses/all',  methods=['GET'])
def get_addresses():
    with open("Results/QuizList.csv", 'r+') as file:
        links = file.read().splitlines()
        file.close()
    return jsonify(links)

@app.route('/addresses/parsed',  methods=['GET'])
def get_parsed():
    with open("Results/ParsedQuizList.csv", 'r+') as file:
        links = file.read().splitlines()
        file.close()
    return jsonify(links)

if __name__ == '__main__':
    app.run()