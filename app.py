from flask import Flask, render_template, request, jsonify
from main import Chatbot, get_progress

app = Flask(__name__)
chatbot = Chatbot()
print("App and chatbot created")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/send_message', methods=['POST'])
def send_message():
    user_input = request.form['user_input']
    
    bot_response = chatbot.generate_output(user_input)

    return jsonify({'bot_response': bot_response})

@app.route('/get_progress', methods=['GET'])
def get_progress_route():
    progress = get_progress()
    return jsonify({'progress': progress})

if __name__ == '__main__':
    app.run(debug=True)
    print("App exited")
