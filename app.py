from flask import Flask, request, jsonify, Response, g, render_template
from dotenv import load_dotenv
import google.generativeai as genai
import mysql.connector
from uuid import uuid4
from datetime import datetime
import os, json
from flask_cors import CORS

load_dotenv()




genai.configure(api_key=os.getenv('GenAPI_KEY'))

app = Flask(__name__)

CORS(app)

db_config={
    "user":os.getenv('USER'),
    "password": os.getenv('PASSWORD'),
    "host": os.getenv('HOST'),
    "database":os.getenv('DATABASE'),
    'raise_on_warnings': True
}



# MySQL configuration


def get_db_connection():
    """ It is for connecting with the database and then make queries , it is a must for all operations"""
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except mysql.connector.Error as e:
        print(f'Error connecting to MySQL: {e}')
        return None

def get_Patient_NameAndId(Name: str):
    """ description:
            For getting patientId by patient's name call this function
        parameters:
         Name(str): the patient name through which to get PatientId 
    """
    conn= get_db_connection()
    cursor= conn.cursor()
    cursor.execute("SELECT PatientId, Name FROM tbl_patient WHERE name = %s", (Name, ))
    rows= cursor.fetchall()
    cursor.close()
    conn.close()
    print("get_Patient_NameAndId: ",str(rows))
    return str(rows)

def see_all_patients(DoctorID: str):
    """
    description:
     Fetches all patients for a given DoctorID from the database. Call it whenever the user wants to know 
     anyof these info of the patient:- PatientId, DoctorID, Name, Age, Registration_date, Address, DateOfBirth	Phone	Email
    
    Parameters:
    - DoctorID (str): The ID of the doctor to fetch patients for.
    
    Returns:
    - list: Sting List of tuples, each tuple representing a row from the tbl_patients table.It will contain PaitentId with other 
        meaning informations.
    """
    try:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM tbl_patients WHERE DoctorID = %s ORDER BY Registration_date DESC", (DoctorID,))
            rows = cursor.fetchall()
            cursor.close()
            conn.close()
            return str(rows)
        else:
            print("Unable to connect to MySQL")
            return None
    except Exception as e:
        print(f"Error fetching patients: {e}")
        return None

def add_patient(Name: str, DateOfBirth: str, Phone: str, Email: str, Address: str, DoctorID: str):
    #print(DateOfBirth)
    """
    Adds a new patient to the database. the doctorId will be from chathistory and if all informations
    nam, age,  phone, email are not given the AI wil ask to give all information
    
    Parameters: (each given by the user)
    - Name (str): Name of the patient.
    - DateOfBirth (str): Date of birth of the patient , you (chat) will convert it to (YYYY,MM,DD) format.
    - Phone (str): Phone number of the patient given .
    - Email (str): Email address of the patient.
    - Address (str): Address of the patient.
    - DoctorID (str): The ID of the doctor adding the patient.
    
    Returns:
    - String : The patients Id with important informations
    """
    birthdate= datetime.strptime(DateOfBirth, '%Y-%m-%d').date()
    try:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            query = "INSERT INTO tbl_patients (PatientId, Name, Age, DateOfBirth, Phone, Email, Address, DoctorID) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
            patient_id = str(uuid4()).replace('-',"")[:30]
            current_date = datetime.now().date()
            Age = current_date.year - birthdate.year - ((current_date.month, current_date.day) < (birthdate.month, birthdate.day))
    
            values = (patient_id, Name, Age, birthdate, Phone, Email, Address, DoctorID)
            cursor.execute(query, values)
            conn.commit()
            cursor.close()
            conn.close()
            #print(values)
            return f"Patient added successfully! ID: {patient_id}, Name: {Name}"
        else:
            print("Unable to connect to MySQL")
            return False
    except Exception as e:
        print(f"Error adding patient: {e}")
        return False

def add_appointment(PatientID: str, AppointmentDateTime: str, Status: str, Notes: str, DoctorID: str):
    """
    Adds a new appointment to the database. Chat model will format the appointmentDateTime as '2024-07-10 10:00:00' (YYYY:MM:DD HH:MM::SS) in order to save it in mysql database
    
    Parameters:
    - PatientID (str): ID of the patient for whom the appointment is being added.
    it will be from patients table that the chat will sotre in history of patient details.
    - AppointmentDateTime (str): Date and time of the appointment .
    - Status (str): ask user to clarify Status. of the appointment (e.g., pending, done).
    - Notes (str): Notes related to the appointment.
    - DoctorID (str): The ID of the doctor adding the appointment. it will be from chat history.
    
    Returns:
    - Sting : Sting of list with appointment id if the appointment was added successfully, False otherwise.
    """
    try:
        conn = mysql.connector.connect(**db_config)
        if conn:
            cursor = conn.cursor()
            query = "INSERT INTO tbl_appointments (AppointmentID, PatientID, DoctorID, AppointmentDateTime, Status, Notes) VALUES (%s, %s, %s, %s, %s, %s)"
            AppointmentID = str(uuid4()).replace('-', '')[:30]
           
            values = (repr(AppointmentID), PatientID, str(DoctorID),AppointmentDateTime, str(Status), str(Notes),)
            cursor.execute(query, values)
            conn.commit()
            cursor.close()
            conn.close()
            print(values)
            return f"Added Successfully. {AppointmentDateTime}, {Status}"
        else:
            print("Unable to connect to MySQL")
            return False
    except Exception as e:
        print(f"Error adding appointment: {e}")
        return False

def all_appointments(DoctorID: str):
    """
    Retrieves all appointments for a given DoctorID from the database.
    
    Parameters:
    - DoctorID (str): The ID of the doctor to fetch appointments for.
    
    Returns:
    - list: List of tuples, each tuple representing a row from the tbl_appointments table.
    """
    try:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            query = "SELECT p.Name, a.* FROM tbl_patients p INNER JOIN tbl_appointments a ON p.PatientID = a.PatientID WHERE p.DoctorID = %s ORDER BY a.AppointmentDateTime DESC"
            cursor.execute(query, (DoctorID,))
            rows = cursor.fetchall()
            cursor.close()
            conn.close()
            return rows
        else:
            print("Unable to connect to MySQL")
            return None
    except Exception as e:
        print(f"Error fetching appointments: {e}")
        return None

def make_prescription(PatientID: str, PrescriptionData: list, Instructions: str, PrescriptionNotes: str, DoctorID: str):
    """
    Adds a new prescription to the database.
    
    Parameters:
    - PatientID (str): ID of the patient for whom the prescription is being made.
    - PrescriptionData (list): List of dictionaries containing medication details.
    - Instructions (str): Instructions related to the prescription.
    - PrescriptionNotes (str): Additional notes related to the prescription.
    - DoctorID (str): The ID of the doctor making the prescription.
    
    Returns:
    - bool: True if the prescription was added successfully, False otherwise.
    """
    try:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            date_issued = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            prescription_id = str(uuid4())
            
            prescription_values = []
            for dose in PrescriptionData:
                prescription_values.append((
                    prescription_id,
                    PatientID,
                    DoctorID,
                    date_issued,
                    dose['MedicationName'],
                    dose['Dosage'],
                    dose['Frequency'],
                    dose['Duration'],
                    dose['Status'],
                    Instructions,
                    PrescriptionNotes
                ))
            
            query = "INSERT INTO tbl_prescription (PrescriptionID, PatientID, DoctorID, DateIssued, MedicationName, Dosage, Frequency, Duration, Status, Instructions, PrescriptionNotes) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            cursor.executemany(query, prescription_values)
            conn.commit()
            cursor.close()
            conn.close()
            return True
        else:
            print("Unable to connect to MySQL")
            return False
    except Exception as e:
        print(f"Error making prescription: {e}")
        return False

def all_prescriptions(DoctorID: str):
    """
    Retrieves all prescriptions for a given DoctorID from the database.
    
    Parameters:
    - DoctorID (str): The ID of the doctor to fetch prescriptions for.
    
    Returns:
    - list: List of tuples, each tuple representing a row from the tbl_prescription table.
    """
    try:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            query = "SELECT p.Name, p.Address, p.Email, pres.* FROM tbl_patients p INNER JOIN tbl_prescription pres ON p.PatientID = pres.PatientID WHERE pres.DoctorID = %s ORDER BY pres.DateIssued DESC"
            cursor.execute(query, (DoctorID,))
            rows = cursor.fetchall()
            cursor.close()
            conn.close()
            return rows
        else:
            print("Unable to connect to MySQL")
            return None
    except Exception as e:
        print(f"Error fetching prescriptions: {e}")
        return None

def update_appointment(AppointmentID: str, Notes: str, Status: str):
    """
    Updates an existing appointment in the database.
    
    Parameters:
    - AppointmentID (str): ID of the appointment to update.
    - Notes (str): Updated notes related to the appointment.
    - Status (str): Updated status of the appointment.
    
    Returns:
    - bool: True if the appointment was updated successfully, False otherwise.
    """
    try:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            query = "UPDATE tbl_appointments SET Notes = %s, Status = %s WHERE AppointmentID = %s"
            values = (Notes, Status, AppointmentID)
            cursor.execute(query, values)
            conn.commit()
            cursor.close()
            conn.close()
            return True
        else:
            print("Unable to connect to MySQL")
            return False
    except Exception as e:
        print(f"Error updating appointment: {e}")
        return False

def seeAllPatients(DoctorID: str, PatientId:str, PatientAge:int, PatientAddress: str, PatientEmail: str, PatientPhone:str):
    
    print("Doctorid : ", DoctorID)
   
    """ to return all the patients from the database for this doctor and the DoctorID will be from the chat history of the chat
        In patients' information there are PatientId, DoctorID, Name Age,	Registration_date, DateOfBirth,	Phone,	Email,	Address.	 
    """
    conn = mysql.connector.connect(**db_config)
    cursor= conn.cursor()
    cursor.execute("SELECT * FROM tbl_patients WHERE DoctorID = %s ", (str(DoctorID),))
    
    rows = cursor.fetchall() 
    conn.close()
   
    return str(rows)

def getWearher(weather: str):
           """ To get the current weather """
           #print(doctor)
           return '34 degree'
 

model= genai.GenerativeModel(model_name='gemini-1.5-flash',
                             tools=[see_all_patients,add_appointment,add_patient, getWearher])
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
                {"text": "You are an AI assistant of MyChamber application"},
                {"text": "Mychamber is a application for doctor to manage their chamber"},
                {"text": f"currently you are serving a doctor called {req['doctor']['Name']} and his other informations are {str(json.dumps(req['doctor']))} "}
            ]
        })
        
        chat= model.start_chat(history=chat_history, enable_automatic_function_calling=True)

        response= chat.send_message(prompt)
        print(req['doctor']['Name'])
        return jsonify(
            response.text
            )
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True, port=5001)