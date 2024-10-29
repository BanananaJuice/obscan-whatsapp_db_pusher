from datetime import datetime
import requests
import psycopg2
from flask import Flask, request
import vonage
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Vonage configuration
VONAGE_API_KEY = os.getenv('VONAGE_API_KEY')
VONAGE_API_SECRET = os.getenv('VONAGE_API_SECRET')
AUTHORIZED_NUMBER = os.getenv('AUTHORIZED_NUMBER')  # Authorized number to send updates
VONAGE_FROM_NUMBER = os.getenv('VONAGE_FROM_NUMBER')

client = vonage.Client(key=VONAGE_API_KEY, secret=VONAGE_API_SECRET)
sms = vonage.Sms(client)

# Database configuration
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')

# Function to connect and insert into the database
def insert_people_fed(people_fed):
    try:
        print("Attempting to connect to database...")
        conn = psycopg2.connect(
            dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
        )
        print("Database connected.")
        cur = conn.cursor()
        
        # Fetch table structure to verify column names
        cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name='HomelessStats'")
        columns = cur.fetchall()
        print("Columns in HomelessStats table:", columns)

        date_now = datetime.now()
        insert_query = """
            INSERT INTO "HomelessStats" ("peopleFed", "date")
            VALUES (%s, %s)
        """
        print(f"Executing query: {insert_query} with values ({people_fed}, {date_now})")
        cur.execute(insert_query, (people_fed, date_now))
        conn.commit()
        print("Data committed successfully.")
        cur.close()
        conn.close()
        print("Connection closed.")
    except Exception as e:
        print("Error inserting into database:", e)

# Flask route for handling incoming SMS messages
@app.route("/sms", methods=["POST"])
def sms_reply():
    from_number = request.form.get("msisdn")
    body = request.form.get("text")

    print(f"Received message from: {from_number} with body: {body}")

    if from_number == AUTHORIZED_NUMBER:
        try:
            people_fed = int(body.strip())
            print(f"Inserting {people_fed} into the database.")
            insert_people_fed(people_fed)
            response_message = f"Recorded {people_fed} people fed on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        except ValueError:
            response_message = "Please send a valid number of people fed."
            print("ValueError: Invalid number received.")
    else:
        response_message = "You are not authorized to send this information."