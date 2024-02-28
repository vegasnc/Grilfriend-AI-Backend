import json

from flask import Flask, request, jsonify
from flask_cors import CORS
from bson import ObjectId
from datetime import datetime
from controllers.user_controller import UserController
from controllers.monster_controller import MonsterController

import controllers.generate_monster as GenerateMonster
import controllers.generate_spell as GenerateSpell

app = Flask(__name__)

CORS(app, methods=['GET', 'POST'], allow_headers=['Content-Type'])

userController = UserController()
monsterController = MonsterController()

# Encodeing the ObjectID and datetime fields as a JSON string
class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId) or isinstance(o, datetime):
            return str(o)
        return json.JSONEncoder.default(self, o)

@app.route('/', methods=['post'])
def get_request():
    return "Good", 200

@app.route('/signup', methods=['post'])
def signup_user():
    # Access the request data
    data = request.get_json()
    
    token, res = userController.signup(data)

    if res == True:
        return jsonify({"status" : True, "token" : token}), 200
    else:
        return jsonify({"status" : False, "result" : token }), 200

@app.route('/login', methods=['post'])
def login_user():
    data = request.get_json()

    token, res = userController.login(data)
    
    if res:
        return jsonify({"status" : True, "token" : token}), 200
    else:
        return jsonify({"status" : False, "result" : token}), 200
    
@app.route('/monster/generate_content', methods=['post'])
def generate_monster():
    data = request.get_json()
    message_list = data["message_list"]
    last_content = data["last_content"]
    content = GenerateMonster.generate_content(message_list, last_content)
    return {
        "result" : content
    }, 200

@app.route('/monster/generate_question', methods=['post'])
def generate_monster_question():
    data = request.get_json()
    message_list = data["message_list"]
    content = GenerateMonster.generate_question(message_list)
    return {
        "result" : content
    }, 200

@app.route('/spell/generate_content', methods=['post'])
def generate_spell():
    data = request.get_json()
    message_list = data["message_list"]
    last_content = data["last_content"]
    content = GenerateSpell.generate_spell(message_list, last_content)
    return {
        "result" : content
    }, 200

@app.route('/spell/generate_question', methods=['post'])
def generate_spell_question():
    data = request.get_json()
    message_list = data["message_list"]
    content = GenerateSpell.generate_question(message_list)
    return {
        "result" : content
    }, 200

@app.route('/get/start_prompt', methods=['post'])
def generate_start_prompt():
    data = request.get_json()
    category = data["category"]
    if category == "monster":
        content = GenerateMonster.get_monster_start_prompt()
    elif category == "spell":
        content = GenerateSpell.get_spell_start_prompt()
    return {
        "result" : content
    }, 200

@app.route('/monster/save_updated_content', methods=['post'])
def save_updated_content():
    data = request.get_json()
    message_list = data["message_list"]
    updated_content = data["updated_content"]
    res = GenerateMonster.save_updated_content(message_list, updated_content )
    return {
        "result": res
    }, 200

@app.route('/hexagon_data', methods=['post'])
def get_hexagon_data():
    res = GenerateMonster.get_hexagon_data()
    return {
        "result": res
    }, 200

@app.route('/create_hexagon', methods=['post'])
def create_hexagon_data():
    GenerateMonster.create_hexagon_Data()
    return {
        "result": True
    }, 200

@app.route('/get/monsters', methods=['post'])
def get_monster_data():
    res = monsterController.get_monsters()
    return {
        "result": res
    }, 200

if __name__ == '__main__':
    print("Server is running on port 5000")
    app.run(debug=False)
