from flask import Flask, request, jsonify, Response, g, render_template
from dotenv import load_dotenv
import google.generativeai as genai
import marko
import os

load_dotenv()


genai.configure(api_key=os.getenv('GenAPI_KEY'))
app = Flask(__name__)




@app.route('/')
def hello():
    return 'Hello World'
def getWearher():
           """ To get the current weather """
           return '34 degree'
 

model= genai.GenerativeModel(model_name='gemini-1.5-flash')
chat_history=[]      

@app.route('/api/chat' , methods=['POST'])
def ChatController():
    
    

    try:
        prompt = request.get_json()['prompt']
        
        chat_history.append({
            "role": "user",
            "parts": [
                {"text": prompt},
                {"text": "You are an AI assistant of MyChamber application"},
                {"text": "Mychamber is a application for doctor to manage their chamber"},
                {"text": "currently you are serving a doctor called Ismail and his other informations are ang:24 "}
            ]
        })
        
        chat= model.start_chat(history=chat_history, enable_automatic_function_calling=True)

        response= chat.send_message(prompt)
        #response.resolve()
        return jsonify({
            "response": response.text
            })
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True, port=5001)