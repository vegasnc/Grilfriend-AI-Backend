from flask import Flask, request
from flask_cors import CORS

import generate_answer

app = Flask(__name__)
CORS(app, methods=[ 'POST', 'GET' ], allow_headers=[ 'Content-Type' ])

@app.route('/get_answer', methods=['POST'])
def get_answer():
    data = request.get_json()
    question = data["question"]
    message = generate_answer.get_response_from_ai(question)

    print(message)
    # get_voice_message(message)
    return {
        "answer": message
    }, 200

if __name__ == "__main__":
    app.run(debug=False)