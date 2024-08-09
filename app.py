from flask import Flask, request, jsonify, Response, g, render_template
from dotenv import load_dotenv
load_dotenv()
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import mysql.connector
from uuid import uuid4
from datetime import datetime
import os, json
import google.cloud.texttospeech as tts
from google.cloud import texttospeech
from flask_cors import CORS
import base64
#telegram
import telegram
import requests

# twilio whatsapp
#from twilio.twiml.messaging_response import MessagingResponse
#from twilio.rest import Client
# Config
TOKEN = os.getenv('bot_token')
TELEGRAM_URL = "https://api.telegram.org/bot{token}".format(token=TOKEN)
WEBHOOK_URL  = os.getenv('url')
client_email= os.getenv('client_email'),
private_key= os.getenv('private_key')

# To retrieve unique user chat ID and group ID, use @IDBot
WHITELISTED_USERS = [5598314527,]
bot = telegram.Bot(token=TOKEN)

from typing import List, Dict, Union

   


from function_module import (GetDoctor,see_all_patients, add_appointment, all_appointments, get_future_appointments,
                                    AppointmentsToday, update_appointment, add_patient, make_prescription,
                                    PatientsRange, get_Patient_Name_Id,get_current_datetime, Send_Email,
                                    getWearher, turnOff_Lights)

genai.configure(api_key=os.getenv('GenAPI_KEY'))

app = Flask(__name__)

CORS(app)

model= genai.GenerativeModel(model_name='gemini-1.5-flash',
                             system_instruction="Your name is Gemi an AI assistant for MyChamber application",
                             tools=[GetDoctor, see_all_patients, add_appointment, all_appointments, get_future_appointments,
                                    AppointmentsToday, update_appointment, add_patient, make_prescription,
                                    PatientsRange, get_Patient_Name_Id,get_current_datetime, Send_Email,
                                    getWearher, turnOff_Lights])


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
            "text": message,
            "text" :"remember the DoctorId given by the user to use it for queries where required"
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
        #print(response)
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
        #print(req['doctor']['Name'])
        return jsonify(
            response.text.replace("**","")
            )
    except Exception as e:
        return jsonify({'error': str(e)})



assistant_history=[]
pvt=os.getenv("GOOGLE_CLOUD_PRIVATE_KEY").replace("\\n","\n")

credentials_info={
     "type": "service_account",
    "project_id": os.getenv("GOOGLE_CLOUD_PROJECT_ID"),
     "private_key_id": os.getenv("GOOGLE_CLOUD_PRIVATE_KEY_ID"),
     "private_key": pvt,
     "client_email": os.getenv("GOOGLE_CLOUD_CLIENT_EMAIL"),
     "client_id": os.getenv("GOOGLE_CLOUD_CLIENT_ID"),
     "auth_uri": "https://accounts.google.com/o/oauth2/auth",
     "token_uri": "https://oauth2.googleapis.com/token",
     "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": os.getenv("GOOGLE_CLOUD_CLIENT_X509_CERT_URL"),
    "universe_domain": "googleapis.com"
  }

@app.route('/api/assistant', methods=['POST'])
def AssistantController():
    client = texttospeech.TextToSpeechClient.from_service_account_info(credentials_info)
    try:
        req = request.get_json()
        text = req['text']
        
        langcode = req['langcode']
        name = req['name']
        
        assistant_history.append({
            "role": "user",
            "parts": [
                
                {"text": "Mychamber is an application for doctor to manage their chamber"},
                {"text": f"currently you are serving a doctor called {req['doctor']['Name']} and his other informations are {str(json.dumps(req['doctor']))} "},
                {"text": text}
            ]
        })
        
        chat= model.start_chat(history = assistant_history, enable_automatic_function_calling=True)

        response= chat.send_message(text, safety_settings={
        'HATE': 'BLOCK_NONE',
        'HARASSMENT': 'BLOCK_NONE',
        'SEXUAL' : 'BLOCK_NONE',
        'DANGEROUS' : 'BLOCK_NONE'
    })
        ai_text= response.text.replace("**","")    
        
        text_input = texttospeech.SynthesisInput(text=ai_text)
        voice_params = texttospeech.VoiceSelectionParams(
        language_code=langcode, name=name
        )
        audio_config = texttospeech.AudioConfig(audio_encoding=tts.AudioEncoding.MP3)

        response = client.synthesize_speech(
        input=text_input,
        voice=voice_params,
        audio_config=audio_config,
      )
        base64_audio = base64.b64encode(response.audio_content).decode('utf-8')
        
        return jsonify({
            'base64Audio': base64_audio
        })
        
    except Exception as e:
        print(e)
        return jsonify({'error': str(e)})


#TWILIO WHATSAPP
"""
account_sid = os.getenv('TWILIO_ACCOUNT_SID')
auth_token = os.getenv('TWILIO_AUTH_TOKEN')

client = Client(account_sid, auth_token)

@app.route('/twiliowebhook', methods=['POST'])
def TwilioController():
    data = request.values
    print("data: ",data)
    incoming_msg = request.values['Body']
    phone_number = request.values['WaId']

    print(incoming_msg, "phone: ", phone_number)
    message = client.messages.create(
                                from_='whatsapp:+14155238886',                  # With Country Code
                                body=incoming_msg,
                                to='whatsapp:' + phone_number                   # With Country Code
                            )
    
    return str(message)

@app.route('/twiliowebhook', methods=['GET'])
def TwilioController():
    return "hi"
"""

# Whatsapp access token
whatsapp_token = os.getenv("ACCESS_TOKEN")
print(whatsapp_token)
# Verify Token defined when configuring the webhook
verify_token = os.getenv('VERIFY_TOKEN')
whatsapp_chat_histories = {}
def send_whatsapp_message(body, message):
    try:
        value = body["entry"][0]["changes"][0]["value"]
        phone_number_id = value["metadata"]["phone_number_id"]
        from_number = value["messages"][0]["from"]
        #whatsapp park
        if from_number not in whatsapp_chat_histories:
            whatsapp_chat_histories[from_number]=[]
    
       
        whatsapp_chat_histories[from_number].append({
             "role":"user",
             "parts":[{
                  "text": message
#                 "text" : f"The DoctorId given by the user:{Doctorid} ane name is {name}"
             }]
        })
        chat= model.start_chat(
            history=whatsapp_chat_histories[from_number],
            enable_automatic_function_calling=True
             )
        response= chat.send_message(message)
    
        AIchat= response.text.replace("**", "")
        
        
        headers = {
            "Authorization": f"Bearer {whatsapp_token}",
            "Content-Type": "application/json",
        }
        
        url = f"https://graph.facebook.com/v20.0/{phone_number_id}/messages?access_token={whatsapp_token}"
        
        data = {
            "messaging_product": "whatsapp",
            "to": from_number,  # Ensure this is the recipient's phone number in E.164 format
            "type": "text",
            "text": {
                "body": AIchat  # Ensure message content is not empty
            },
        }
        
        response = requests.post(url, json=data, headers=headers)
        
        try:
            response.raise_for_status()
            print("WhatsApp message response sent")
        except requests.exceptions.HTTPError as err:
            print(f"HTTP error occurred: {err}")
            #if recipient not present in the whatsapp business api allowed list:
            """ HTTP error occurred: 400 Client Error: Bad Request for url:
            https://graph.facebook.com/v20.0/384460164747685/messages?access_token={token}
            Response content: {"error":{"message":"(#131030) Recipient phone number not in allowed list",
            "type":"OAuthException","code":131030,"error_data":{"messaging_product":"whatsapp",
            "details":"Recipient phone number not in allowed list: Add recipient phone number to recipient list and try again."},
            "fbtrace_id":"AFXVb2PxwDZXqmWDadIFvld"}} """
            
            print(f"Response content: {response.text}")  # Output response content for debugging
        except Exception as err:
            print(f"Other error occurred: {err}")

    except KeyError as e:
        print(f"Missing expected data in the request body: {e}")
#whatsapp cloud api

def handle_whatsapp_message(body):
     
    message = body["entry"][0]["changes"][0]["value"]["messages"][0]
    if message["type"] == "text":
        message_body = message["text"]["body"]
        send_whatsapp_message(body, message_body)

# handle incoming webhook messages
def handle_message(request):
    # Parse Request body in json format
    body = request.get_json()
  
    try:
        if body.get("object"):
            if (
                body.get("entry")
                and body["entry"][0].get("changes")
                and body["entry"][0]["changes"][0].get("value")
                and body["entry"][0]["changes"][0]["value"].get("messages")
                and body["entry"][0]["changes"][0]["value"]["messages"][0]
            ):
                handle_whatsapp_message(body)
            return jsonify({"status": "ok"}), 200
        else:
            return (
                jsonify({"status": "error", "message": "Not a WhatsApp API event"}),
                404,
            )
    except Exception as e:
        print(f"unknown error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

def verify(request):
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    # Check if a token and mode were sent
    if mode and token:
        if mode == "subscribe" and token == verify_token:
            print("WEBHOOK_VERIFIED")
            return challenge, 200
        else:
            # Responds with '403 Forbidden' if verify tokens do not match
            print("VERIFICATION_FAILED")
            return jsonify({"status": "error", "message": "Verification failed"}), 403
    else:
        # Responds with '400 Bad Request' if verify tokens do not match
        print("MISSING_PARAMETER")
        return jsonify({"status": "error", "message": "Missing parameters"}), 400

# Accepts POST and GET requests at /webhook endpoint
@app.route("/webhook", methods=["POST", "GET"])
def webhook():
    if request.method == "GET":
        return verify(request)
    elif request.method == "POST":
        
        return handle_message(request)




if __name__ == '__main__':
    app.run(debug=True, port=5001)