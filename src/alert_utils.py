# alert_utils.py
import winsound
from twilio.rest import Client
from datetime import datetime
import os
from  dotenv import load_dotenv

# Buzzer alert
def play_buzzer():
    duration = 1000  # 1 second
    freq = 600       # Hz
    winsound.Beep(freq, duration)

# WhatsApp alert via Twilio sandbox
def send_whatsapp_alert(message):
    ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
    AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
    WHATSAPP_FROM = os.getenv("WHATSAPP_FROM")
    WHATSAPP_TO = os.getenv("WHATSAPP_TO")   
    client = Client(ACCOUNT_SID, AUTH_TOKEN)
    client.messages.create(
        body=message,
        from_=WHATSAPP_FROM,
        to=WHATSAPP_TO
    )
    print(f"📩 WhatsApp alert sent at {datetime.now()}")
