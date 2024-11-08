
from flask import Flask, request, jsonify, Response, g, render_template
from dotenv import load_dotenv
import google.generativeai as genai
import mysql.connector
from uuid import uuid4
from datetime import datetime
import os, json
from flask_cors import CORS


from typing import List, Dict, Union
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os, json



load_dotenv()

db_config={
    "host": os.getenv('DB_INSTANCE'),
    "user":os.getenv('DB_USER'),
    "password": os.getenv('DB_PASSWORD'),
    "database":os.getenv('DATABASE'),
    #"port":os.getenv('DB_PORT'),
    'raise_on_warnings': True
}


def get_current_datetime(Data:str):
    """
    Returns the current date and time. Use this date for to determine future and past dates and use the date
    for getting any patient data related to date, if the user asks.
    
    Returns:
    str: Formatted current date and time string.
    """
    return f"current date time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

s = smtplib.SMTP('smtp.gmail.com', 587)  # Replace with your SMTP server and port

sender_email= os.getenv("sender_email")
sender_email_pass= os.getenv("sender_email_Pass")

"""
s.login() :This took me days to solve  a error, passing variable to login inside Send_Main() 
gives:- Error sending email: (535, b'5.7.8 Username and Password not accepted. For more information, go to\n5.7.8  https://support.google.com/mail/?p=BadCredentials
it has to be hardcoded or called outside the Send_Mail() function, since i'm calling os.getenv() it had to be
called outside.
"""

def Send_Email(EmailAddress:str, EmailDescription:str, EmailSubject:str):
    """
     Send email to user.
    Parameters:
    EmailAddress (str): python List of Patient Email address. Emails should be in this format ["test@gmail.com"] wrapped no extra symbol.
    EmailDescription (str):A suitable description
    EmailSubject: set a appropriate subject for the email
    Returns:
    String : Confirmation if the email has been sent or not
    
    """
    try:
        s.starttls()
        s.login(sender_email, sender_email_pass) 
        EmailDescription= EmailDescription  
        print("Emails:", EmailAddress)
        #print("Descrip: ", EmailDescription)
        
        for dest in EmailAddress:
             html_content = """
            <html>
            <head>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        color: #333;
                    }}
                    .container {{
                        width: 80%;
                        margin: 0 auto;
                        padding: 20px;
                        background-color: #f9f9f9;
                        border: 1px solid #ddd;
                        border-radius: 5px;
                    }}
                    h1 {{
                        color: #2c3e50;
                    }}
                    p {{
                        font-size: 16px;
                    }}
                    .footer {{
                        margin-top: 20px;
                        font-size: 14px;
                        color: #888;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>Important Update</h1>
                    <p>{}</p>
                    <div class="footer">
                        <p>Powered by Google's Gemini</p>
                    </div>
                </div>
            </body>
            </html>
            """.format(EmailDescription)

            # Create MIMEText object for HTML content
             msg = MIMEMultipart()
             msg['Subject'] = EmailSubject  # Customize the subject line as needed
             msg['From'] = sender_email
             msg['To'] = dest
             msg.attach(MIMEText(html_content, 'html'))
            # Send the email
             s.sendmail(sender_email, dest, msg.as_string())
             print("Email sent to:", dest)
            
        
        s.quit()
        return "Message sent"
    
    except Exception as e:
        print("Error sending email:", str(e))
        return "Message not sent because of error"

def get_db_connection():
    """ It is for connecting with the database and then make queries , it is a must for all operations"""
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except mysql.connector.Error as e:
        print(f'Error connecting to MySQL: {e}')
        return None


DoctorID= "None"
Name ="None"

def GetDoctor(DoctorId:str):
    """
    description:
            Call this function whenever the user gives a DoctorId.
            For getting Name of Doctor using the DoctorId given by the user.          
    Parameters:
         DoctorId(str): The ID of the doctor given by the user.
        
    Returns:
           - String: A string with Doctor Name
    """
    try:
        DoctorID= DoctorId
        conn= get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT Name FROM tbl_doctors WHERE DoctorID = %s ", (DoctorID,))
        rows = cursor.fetchall()
        print(rows[0])
        Name= rows[0]
        print(Name)
        cursor.close()
        conn.close()
        return str(rows)
    except Exception as e:
        print(f"Error fetching patients: {e}")
        return "Error"
    
    

def get_Patient_Name_Id(PatientName: str, DoctorId: str)->str:
    """ 
    description:
            For getting patientId for a given name .Use this PatientId to make prescription
            or appointment or sending email or anywhere necessary.
            
    Parameters:
         PatientName(str): the patient name through which to get PatientId 
         DoctorId(str): The ID of the doctor to fetch patients for. Get this from chat history.
        
    Returns:
           - String: A string with patientId and name
    """
    #print(PatientName)
    try:
         conn= mysql.connector.connect(**db_config)
         if conn: 
             cursor= conn.cursor(dictionary=True)
             query = "SELECT PatientId, Name, Email FROM tbl_patients WHERE LOWER(Name) LIKE LOWER(%s) AND DoctorId = %s"
             cursor.execute(query, (str(PatientName), str(DoctorId), ))
             rows = cursor.fetchall()
            
             cursor.close()
             conn.close()
            
             if rows:
                
                res= str(json.dumps(rows)).replace("[","'").replace("]","'")
                print(res)
                #json.dumps(str(result))
                return res
             else:
                 print("Error getting Id")
                 return "Patient not found"
         else:
            print("Unable to connect to MySQL")
            return "Error"
    except Exception as e:
        print(f"Error fetching patients: {e}")
        return "Error"
    
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
            return "Error"
    except Exception as e:
        print(f"Error fetching patients: {e}")
        return "Error"

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
            return f"Added Successfully. AppointmentId:{AppointmentID} {AppointmentDateTime}, {Status}"
        else:
            print("Unable to connect to MySQL")
            return False
    except Exception as e:
        print(f"Error adding appointment: {e}")
        return False

def all_appointments(DoctorID: str):
    """
    Retrieves all appointments for a given DoctorID from the database. Use these data to reveal  
     previous appointments in accordance with date for the query response.
    
    Parameters:
    - DoctorID (str): The ID of the doctor to fetch appointments for.
    
    Returns:
    - list: List of tuples, each tuple representing a row from the tbl_appointments table.
    """
    try:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            query = "SELECT p.Name, a.AppointmentDateTime ,a.Status, a.Notes FROM tbl_patients p INNER JOIN tbl_appointments a ON p.PatientID = a.PatientID WHERE p.DoctorID = %s ORDER BY a.AppointmentDateTime DESC"
            cursor.execute(query, (DoctorID,))
            rows = cursor.fetchall()
            cursor.close()
            conn.close()
            return f"appointments: {rows}"
        else:
            print("Unable to connect to MySQL")
            return None
    except Exception as e:
        print(f"Error fetching appointments: {e}")
        return None

def get_future_appointments(DoctorID:str):
    """
    Retrieves future appointments for a given DoctorID from the database.

    Parameters:
    DoctorID (int): The ID of the doctor.

    Returns:
    String : List of future appointment records.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        #print(current_datetime)
        query = """
        SELECT p.Name, p.Email, p.PatientId, a.AppointmentDateTime 
        FROM tbl_patients p
        INNER JOIN tbl_appointments AS a ON p.PatientID = a.PatientID
        WHERE p.DoctorID = %s AND a.AppointmentDateTime > %s
        ORDER BY AppointmentDateTime
        """
        cursor.execute(query, (DoctorID, current_datetime))
        future_appointments = cursor.fetchall()

        cursor.close()
        conn.close()

        return f"Future appointments: {future_appointments}"

    except mysql.connector.Error as err:
        print("Error retrieving future appointments:", err)
        return "Error"

#AllowedType = Union[int, float, bool, str, List['AllowedType'], Dict[str, 'AllowedType']]
def make_prescription(PatientID: str, MedicationName: str,Dosage:str,Frequency:str, Duration:str, Status:str, Instructions: str, PrescriptionNotes: str, DoctorID: str) ->str:
    """
    Adds a new prescription to the database. For medicine ask user to specify 'MedicationName',
                    'Dosage',
                    'Frequency',
                    'Duration',
                    'Status',
    
    Parameters:
    - PatientID (str): ID of the patient for whom the prescription is being made.
    - MedicationName (str): Name of the medication.
    - Dosage (str): Dosage amount and unit (e.g., '500mg', '1 tablet').
    - Frequency (str): Frequency of taking the medication (e.g., 'Twice daily', 'Once a day').
    - Duration (str): Duration of the prescription (e.g., '5 days', '2 weeks').
    - Status (str): Status of the prescription (e.g., 'Active', 'Inactive').
    - Instructions (str): Instructions related to the prescription.
    - PrescriptionNotes (str): Additional notes related to the prescription.
    - DoctorID (str): ID of the doctor making the prescription got from the chat history.
    
    Returns:
    - string: The list of prescription with necessary details
    """
    try:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            Date_Issued = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            prescription_id = str(uuid4()).replace('-',"")[:30]
            print(prescription_id)
           # prescription_values = []
            #for dose in PrescriptionData:
            #    prescription_values.append((
            #        prescription_id,
            #        PatientID,
            #        DoctorID,
            #        date_issued,
            #        dose['MedicationName'],
            #        dose['Dosage'],
            #        dose['Frequency'],
            #        dose['Duration'],
            #        dose['Status'],
            #        Instructions,
            #    PrescriptionNotes
            # ))
            
            query = "INSERT INTO tbl_prescription (PrescriptionID, PatientID, DoctorID, DateIssued, MedicationName, Dosage, Frequency, Duration, Status, Instructions, PrescriptionNotes) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            cursor.execute(query, ( prescription_id ,PatientID, DoctorID, Date_Issued, MedicationName, Dosage, Frequency, Duration, Status, Instructions, PrescriptionNotes,))
            rows = cursor.fetchall()
            conn.commit()
            cursor.close()
            conn.close()
            print(prescription_id ,PatientID, DoctorID, Date_Issued, MedicationName, Dosage, Frequency, Duration, Status, Instructions, PrescriptionNotes)
            return f"Added prescription with values: {rows}"
        else:
            print("Unable to connect to MySQL")
            return "Error"
    except Exception as e:
        print(f"Error making prescription: {e}")
        return "Could not make"

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

def update_appointment(AppointmentID: str,  Status: str):
    """
    Updates an existing appointment in the database. 
    And for AppointmentID do not ask the user for it instead, get it using AppointmentsToday for a patient function to update
    
    Parameters:
    - AppointmentID (str): ID of the appointment to update.
    - Notes (str): Updated notes related to the appointment.
    - Status (str): Updated status of the appointment.
    
    Returns:
    - Sring: Detalis of what update was made
    """
    try:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            query = "UPDATE tbl_appointments SET  Status = %s WHERE AppointmentID = %s"
            values = (Status, AppointmentID,)
            cursor.execute(query, values)
            conn.commit()
            cursor.close()
            conn.close()
            return f"Status updated to {Status}"
        else:
            print("Unable to connect to MySQL")
            return "Error"
    except Exception as e:
        print(f"Error updating appointment: {e}")
        return "Error"

#def seeAllPatients(DoctorID: str, PatientId:str, PatientAge:int, PatientAddress: str, PatientEmail: str, PatientPhone:str):
    
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


def AppointmentsToday(DoctorID:str):
    """
    Fetch appointments for today for the doctor. Also use the appointmentId from here to update the Appoinement of a patient.
    
    Parameters:
    DoctorID (str): The ID of the doctor.
    
    Returns:
    String: List of appointment records.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = """
        SELECT p.Name, p.Address, p.Age, p.Email, a.*
        FROM tbl_patients p
        INNER JOIN tbl_appointments AS a ON p.PatientID = a.PatientID
        WHERE p.DoctorID = %s AND DATE(a.AppointmentDateTime) = CURDATE()
        """
        cursor.execute(query, (DoctorID,))
        rows = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return f" today's appointments are: {rows}"
    
    except mysql.connector.Error as err:
        print("Error getting appointments:", err)
        return "Error"


def PatientsRange(DoctorID: str):
    """
    Count patients in different age ranges for statistical data.
    
    Parameters:
    DoctorID (str): The ID of the doctor.
    
    Returns:
    String : List of age range counts.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = """
        SELECT 
            COUNT(*) as count,
            CASE
                WHEN age BETWEEN 0 AND 12 THEN 'Infants and Children'
                WHEN age BETWEEN 13 AND 18 THEN 'Adolescents'
                WHEN age BETWEEN 19 AND 30 THEN 'Young Adults'
                WHEN age BETWEEN 31 AND 50 THEN 'Adults'
                WHEN age BETWEEN 51 AND 65 THEN 'Middle-Aged Adults'
                WHEN age BETWEEN 66 AND 80 THEN 'Seniors'
                ELSE 'Elderly'
            END as age_range
        FROM 
            tbl_patients WHERE DoctorID = %s
        GROUP BY 
            CASE
                WHEN age BETWEEN 0 AND 12 THEN 'Infants and Children'
                WHEN age BETWEEN 13 AND 18 THEN 'Adolescents'
                WHEN age BETWEEN 19 AND 30 THEN 'Young Adults'
                WHEN age BETWEEN 31 AND 50 THEN 'Adults'
                WHEN age BETWEEN 51 AND 65 THEN 'Middle-Aged Adults'
                WHEN age BETWEEN 66 AND 80 THEN 'Seniors'
                ELSE 'Elderly'
            END
        ORDER BY 
            age_range
        """
        cursor.execute(query, (DoctorID,))
        rows = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return f"statistical data on patients: {rows}"
    
    except mysql.connector.Error as err:
        print("Error counting patients:", err)
        return None


def getWearher(weather: str):
           """ To get the current weather """
           #print(doctor)
           return '34 degree'
 
 
def turnOff_Lights(description: str):
    """
    Description:
        When the user leaves the Chamber Turn of all the room lights.
    """
    return "Lights switched off"

