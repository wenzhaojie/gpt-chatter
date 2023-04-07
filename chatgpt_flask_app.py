import os
from flask import Flask, request, jsonify, render_template, session
from flask_cors import CORS
import openai
import html2text
from bs4 import BeautifulSoup

app = Flask(__name__)
CORS(app)
app.secret_key = os.urandom(24)

openai.api_key = os.getenv("OPENAI_API_KEY")

global_history = []

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

def save_chat_to_markdown(chat_history, filename):
    markdown_content = ""
    markdown_converter = html2text.HTML2Text()
    markdown_converter.ignore_links = False

    for message in chat_history:
        user, text = message
        user_formatted = f"**{user}:**"
        soup = BeautifulSoup(text, 'html.parser')
        text_md = markdown_converter.handle(str(soup)).strip()
        markdown_content += f"{user_formatted} {text_md}\n\n"

    with open(filename, "w", encoding="utf-8") as output_file:
        output_file.write(markdown_content)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_input = data.get('message', '')
    user_id = data.get('user_id', '')

    if 'chat_history' not in session:
        session['chat_history'] = []

    session['chat_history'].append(('You', user_input))
    chatgpt_response = chat_with_gpt(user_input)
    session['chat_history'].append(('ChatGPT', chatgpt_response))
    global_history.append(('You', user_input))
    global_history.append(('ChatGPT', chatgpt_response))

    return jsonify({"response": chatgpt_response, "chat_history": session['chat_history']})

@app.route('/save_history', methods=['POST'])
def save_history():
    output_filename = "chat_log.md"
    save_chat_to_markdown(global_history, output_filename)
    return jsonify({"message": f"Chat log saved as Markdown in {output_filename}"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)