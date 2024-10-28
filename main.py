from datetime import datetime
import requests
import psycopg2
from twilio.rest import Client
from flask import Flask, request

# Initialize Flask app
app = Flask(__name__)

# Twilio configuration
TWILIO_ACCOUNT_SID = 'ACef3766228abac34c523e5dcdddb7c838'
TWILIO_AUTH_TOKEN = '5495b2358216f3b0528330748adf5671'
TWILIO_PHONE_NUMBER = 'whatsapp:+14155238886'
AUTHORIZED_NUMBER = 'whatsapp:+27605467755'  # Authorized number to send updates

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Database configuration
DB_NAME = "postgres"
DB_USER = "postgres.qdpzxholuqupwgcwulog"
DB_PASSWORD = "HomelessPeople6969420"
DB_HOST = "aws-0-eu-west-2.pooler.supabase.com"
DB_PORT = "5432"

# Function to connect and insert into the database
def insert_people_fed(people_fed):
    try:
        print("Attempting to connect to database...")
        conn = psycopg2.connect(
            dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
        )
        print("Database connected.")
        cur = conn.cursor()

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

# Flask route for handling incoming WhatsApp messages
@app.route("/sms", methods=["POST"])
def sms_reply():
    from_number = request.form.get("From")
    body = request.form.get("Body")

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
        print("Unauthorized number.")

    client.messages.create(
        body=response_message,
        from_=TWILIO_PHONE_NUMBER,
        to=from_number
    )

    return "", 200

if __name__ == "__main__":
    app.run(debug=True, port=5000)