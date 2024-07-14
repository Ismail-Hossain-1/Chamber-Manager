from flask import Flask, request, jsonify, Response, g, render_template
from dotenv import load_dotenv
load_dotenv()
import google.generativeai as genai
import mysql.connector
from uuid import uuid4
from datetime import datetime
import os, json
from flask_cors import CORS

#telegram
import telegram
import requests
# Config
TOKEN = os.getenv('bot_token')
TELEGRAM_URL = "https://api.telegram.org/bot{token}".format(token=TOKEN)
WEBHOOK_URL  = os.getenv('url')

# To retrieve unique user chat ID and group ID, use @IDBot
WHITELISTED_USERS = [5598314527,]
bot = telegram.Bot(token=TOKEN)

from typing import List, Dict, Union
from function_module import * 
"""(see_all_patients, add_appointment, all_appointments, get_future_appointments,
                                    AppointmentsToday, update_appointment, add_patient, make_prescription,
                                    PatientsRange, get_Patient_Name_Id,get_current_datetime, Send_Email,
                                    getWearher) """

genai.configure(api_key=os.getenv('GenAPI_KEY'))

app = Flask(__name__)

CORS(app)

model= genai.GenerativeModel(model_name='gemini-1.5-flash',
                             system_instruction="Your name is Gemi an AI assistant for MyChamber application",
                             tools=[see_all_patients, add_appointment, all_appointments, get_future_appointments,
                                    AppointmentsToday, update_appointment, add_patient, make_prescription,
                                    PatientsRange, get_Patient_Name_Id,get_current_datetime, Send_Email,
                                    getWearher])


telegram_chat_histories = {}

def sendmessage(chat_id, prompt):
    # As the bot is searchable and visble by public.
    # Limit the response of bot to only specific chat IDs.
    authorised = True if chat_id in WHITELISTED_USERS else False
                
    message = prompt
    
    

    if chat_id not in telegram_chat_histories:
        telegram_chat_histories[chat_id]=[]
    
    telegram_chat_histories[chat_id].append({
        "role":"user",
        "parts":[{
            "text": message
        }]
    })
    chat= model.start_chat(
        history=telegram_chat_histories[chat_id],
        enable_automatic_function_calling=True
        )
    response= chat.send_message(message)
    
    AIchat= response.text.replace("**", "")
    
    if not authorised:
        AIchat = "You're not authorised."
    url = "{telegram_url}/sendMessage".format(telegram_url=TELEGRAM_URL)
    
    payload = {
        "text": AIchat,
        "chat_id": chat_id
        }
    
    resp = requests.get(url,params=payload)
    #print('from send Message ', resp.json())

@app.route("/", methods=["POST","GET"])
def index():
    if(request.method == "POST"):
        response = request.get_json()
        print(response)
        
       
        # To run only if 'message' exist in response.
        if 'message' in response:

            # To not response to other bots in the same group chat
            if 'entities' not in response['message']:
            
                chat_id = response["message"]["chat"]["id"]
                prompt=response["message"]["text"]
                sendmessage(chat_id, prompt)

    return "Success"

@app.route("/setwebhook/")
def setwebhook():
    s = requests.get("{telegram_url}/setWebhook?url={webhook_url}".format(telegram_url=TELEGRAM_URL,webhook_url=WEBHOOK_URL))
    print(s)
  
    if s:
        return "Success"
    else:
        return "Fail"




chat_history=[]      
@app.route('/api/chat' , methods=['POST'])
def ChatController():
    #if(doctor!=''): print(doctor)
    

    try:
        req = request.get_json()
        prompt= req['prompt']
        
        chat_history.append({
            "role": "user",
            "parts": [
                {"text": prompt},
                {"text": "Mychamber is an application for doctor to manage their chamber"},
                {"text": f"currently you are serving a doctor called {req['doctor']['Name']} and his other informations are {str(json.dumps(req['doctor']))} "}
            ]
        })
        
        chat= model.start_chat(history=chat_history, enable_automatic_function_calling=True)

        response= chat.send_message(prompt)
        print(req['doctor']['Name'])
        return jsonify(
            response.text.replace("**","")
            )
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True, port=5001)