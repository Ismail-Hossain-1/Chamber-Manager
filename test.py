from flask import Flask, request, jsonify, Response, g, render_template
from dotenv import load_dotenv
import google.generativeai as genai
import marko
import os
import smtplib
s= smtplib.SMTP("localhost")
print(s.help())


load_dotenv()


genai.configure(api_key=os.getenv('GenAPI_KEY'))
app = Flask(__name__)


def get_weather(request:str):
    """returns weather information"""
    
    return {"weather":"34 degree"}

def subtract(a: float, b: float):
    """returns a - b."""
    return a - b

def multiply(a: float, b: float):
    """returns a * b."""
    return (a * b) - 8 

def divide(a: float, b: float):
    """returns a / b."""
    return a / b

# Initialize generative model
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    tools=[get_weather,subtract, multiply, divide]
)
chat = model.start_chat(enable_automatic_function_calling=True)

# Route for interacting with the generative model
@app.route('/ask', methods=['POST'])
def ask_question():
    data = request.get_json()
    question = data['question']
    print(question)

    try:
        # Send message to the generative model chat
        response = chat.send_message(question)
        text = response.text

        return jsonify({"response": text})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=8080)