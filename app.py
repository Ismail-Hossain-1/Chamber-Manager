from flask import Flask, request, jsonify, Response, g, render_template
from dotenv import load_dotenv
import google.generativeai as genai
from flask_mysqldb import MySQL
import os

load_dotenv()




genai.configure(api_key=os.getenv('GenAPI_KEY'))
app = Flask(__name__)


app.config['MYSQL_HOST'] = os.getenv('HOST')
app.config['MYSQL_USER'] = os.getenv('USER') # Replace with your MySQL username
app.config['MYSQL_PASSWORD'] = os.getenv('PASSWORD') # Replace with your MySQL password
app.config['MYSQL_DB'] = os.getenv('DATABASE')  # Replace with your database name
app.config['MYSQL_CURSORCLASS'] = 'DictCursor' 

mysql = MySQL(app)

if mysql:
    print()
    
else :
    print("MySql not connected")

doctor=''
@app.route('/')
def hello():
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM tbl_doctors')
    results = cur.fetchall()
    cur.close()
    doctor=results
    print(results)
    return 'Hello World'
def getWearher(weather: str):
           """ To get the current weather """
           #print(doctor)
           return '34 degree'
 

model= genai.GenerativeModel(model_name='gemini-1.5-flash', tools=[getWearher])
chat_history=[]      

@app.route('/api/chat' , methods=['POST'])
def ChatController():
    if(doctor!=''): print(doctor)
    

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
        
        return jsonify({
            "response": response.text
            })
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True, port=5001)