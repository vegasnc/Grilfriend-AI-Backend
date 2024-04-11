import json
import sentry_sdk

from flask import Flask, request, jsonify
from flask_cors import CORS
from bson import ObjectId
from datetime import datetime
from controllers.user_controller import UserController
from controllers.monster_controller import MonsterController
from dotenv import dotenv_values
from posthog import Posthog
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk import capture_exception

import controllers.generate_monster as GenerateMonster
import controllers.generate_spell as GenerateSpell
import controllers.generate_background as GenerateBackground
import controllers.generate_magic_item as GenerateMagicItem
import controllers.generate_npc as GenerateNPC

sentry_sdk.init(
    dsn="https://fb4c42ae8a1663b1494bb91ddd1d94f7@o4506428658286592.ingest.us.sentry.io/4506443734450176",
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    traces_sample_rate=1.0,
    # Set profiles_sample_rate to 1.0 to profile 100%
    # of sampled transactions.
    # We recommend adjusting this value in production.
    profiles_sample_rate=1.0,
    integrations=[FlaskIntegration()]
)


app = Flask(__name__)

CORS(app, methods=['GET', 'POST'], allow_headers=['Content-Type'])

env_vars = dotenv_values('.env')
POSTHOG_KEY = env_vars["POSTHOG_KEY"]
POSTHOG_HOST = env_vars["POSTHOG_HOST"]
# Initialize PostHog
posthog = Posthog(POSTHOG_KEY, host=POSTHOG_HOST)
posthog.debug = True

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
    posthog.capture(
        "backend_user_sign_up", 
        "user_signed_up"
    )
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

    posthog.capture(
        "backend_user_sign_in", 
        "user_signed_in"
    )

    token, res = userController.login(data)
    
    if res:
        return jsonify({"status" : True, "token" : token}), 200
    else:
        return jsonify({"status" : False, "result" : token}), 200
    
@app.route('/monster/generate_content', methods=['post'])
def generate_monster():
    posthog.capture(
        "backend_generate_monster_content", 
        "generate_monster_content"
    )
    data = request.get_json()
    message_list = data["message_list"]
    last_content = data["last_content"]
    monster_content, dalle_prompt  = GenerateMonster.generate_content(message_list, last_content)
    return {
        "monster_content" : monster_content,
        "dalle_prompt" : dalle_prompt
    }, 200

@app.route('/monster/generate_question', methods=['post'])
def generate_monster_question():
    posthog.capture(
        "backend_generate_monster_question", 
        "generate_monster_question"
    )
    data = request.get_json()
    message_list = data["message_list"]
    content = GenerateMonster.generate_question(message_list)
    return {
        "result" : content
    }, 200

@app.route('/spell/generate_content', methods=['post'])
def generate_spell():
    posthog.capture(
        "backend_generate_spell_content", 
        "generate_spell_content"
    )
    data = request.get_json()
    message_list = data["message_list"]
    last_content = data["last_content"]
    content = GenerateSpell.generate_spell(message_list, last_content)
    return {
        "result" : content
    }, 200

@app.route('/spell/generate_question', methods=['post'])
def generate_spell_question():
    posthog.capture(
        "backend_generate_spell_question", 
        "generate_spell_question"
    )
    data = request.get_json()
    message_list = data["message_list"]
    content = GenerateSpell.generate_question(message_list)
    return {
        "result" : content
    }, 200

@app.route('/background/generate_content', methods=['post'])
def generate_background():
    posthog.capture(
        "backend_generate_background_content", 
        "generate_background_content"
    )
    data = request.get_json()
    message_list = data["message_list"]
    last_content = data["last_content"]
    content = GenerateBackground.generate_background(message_list, last_content)
    return {
        "result" : content
    }, 200

@app.route('/background/generate_question', methods=['post'])
def generate_background_question():
    posthog.capture(
        "backend_generate_background_question", 
        "generate_background_question"
    )
    data = request.get_json()
    message_list = data["message_list"]
    content = GenerateBackground.generate_question(message_list)
    return {
        "result" : content
    }, 200

@app.route('/magic_item/generate_content', methods=['post'])
def generate_magic_item():
    posthog.capture(
        "backend_generate_magic_item_content", 
        "generate_magic_item_content"
    )
    data = request.get_json()
    message_list = data["message_list"]
    last_content = data["last_content"]
    content = GenerateMagicItem.generate_magic_item(message_list, last_content)
    return {
        "result" : content
    }, 200

@app.route('/magic_item/generate_question', methods=['post'])
def generate_magic_item_question():
    posthog.capture(
        "backend_generate_magic_item_question", 
        "generate_magic_item_question"
    )
    data = request.get_json()
    message_list = data["message_list"]
    content = GenerateMagicItem.generate_question(message_list)
    return {
        "result" : content
    }, 200

@app.route('/npc/generate_content', methods=['post'])
def generate_npc():
    posthog.capture(
        "backend_generate_npc_content", 
        "generate_npc_content"
    )
    data = request.get_json()
    message_list = data["message_list"]
    last_content = data["last_content"]
    content = GenerateNPC.generate_content(message_list, last_content)
    return {
        "result" : content
    }, 200

@app.route('/npc/generate_question', methods=['post'])
def generate_npc_question():
    posthog.capture(
        "backend_generate_npc_question", 
        "generate_npc_question"
    )
    data = request.get_json()
    message_list = data["message_list"]
    content = GenerateNPC.generate_question(message_list)
    return {
        "result" : content
    }, 200

@app.route('/get/start_prompt', methods=['post'])
def generate_start_prompt():
    posthog.capture(
        "backend_generate_start_prompt", 
        "generate_start_prompt"
    )
    data = request.get_json()

    category = data["category"]
    if category == "monster":
        content = GenerateMonster.get_monster_start_prompt()
    elif category == "spell":
        content = GenerateSpell.get_spell_start_prompt()
    elif category == "background":
        content = GenerateBackground.get_background_start_prompt()
    elif category == "magic_item":
        content = GenerateMagicItem.get_magic_item_start_prompt()
    elif category == "npc":
        content = GenerateNPC.get_npc_start_prompt()

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

@app.errorhandler(Exception)
def handle_exception(e):
    capture_exception(e)
    print(f"Error captured : {e}")

if __name__ == '__main__':
    print("Server is running on port 5000")
    app.run(debug=False)
