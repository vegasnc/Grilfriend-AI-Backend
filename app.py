from flask import Flask, request
from flask_cors import CORS
from dotenv import dotenv_values

import generate_answer

app = Flask(__name__)
CORS(app, methods=[ 'POST', 'GET' ], allow_headers=[ 'Content-Type' ])

env_vars = dotenv_values('.env')

@app.route('/get_answer', methods=['POST'])
def get_answer():
    # Access the request data
    data = request.get_json()
    question = data["question"]
    history_id = data["history_id"]

    # Generate answer using ChatGPT
    s_data, history_id = generate_answer.get_answer(question, history_id)

    if s_data == None:
        return {
            "answer": "I'm sorry. Please try again later.",
            "history_id": history_id
        }, 200
    else:
        return {
            "answer": s_data,
            "history_id": history_id
        }, 200  
    
if __name__ == '__main__':
    print("Server is running 5000")
    app.run(debug=True)
