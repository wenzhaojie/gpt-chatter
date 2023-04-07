import os
import json
import openai
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

openai.api_key = os.getenv("OPENAI_API_KEY")

def chat_with_gpt(prompt, model="text-davinci-002"):
    completions = openai.Completion.create(
        engine=model,
        prompt=prompt,
        max_tokens=100,
        n=1,
        stop=None,
        temperature=0.5,
    )
    response = completions.choices[0].text.strip()
    return response

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json['user_input']
    chatgpt_response = chat_with_gpt(user_input)
    return jsonify(response=chatgpt_response)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
