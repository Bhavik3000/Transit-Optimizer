import smtplib
import requests
import asyncio
from email.mime.text import MIMEText
from ai_service import AIService
from transit_service import TransitService
from calendar_desktop_test import CalendarService
from dotenv import load_dotenv
import os

load_dotenv()

# --- Config --- #
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")
RECEIVER_SMS = os.getenv("RECEIVER_SMS")
STOP_ID = os.getenv("STOP_ID")


def send_sms(message_body):
    msg = MIMEText(message_body)
    msg['Subject'] = "Transit Bot" 
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECEIVER_SMS
    
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
        print("⏰ Morning commute SMS sent successfully!")
    except Exception as e:
        print(f"Failed to send SMS: {e}")
        
def run_morning_routine():

    async def generate_and_send():
        print("Gathering data for morning routine...")
        
        try:
            res = requests.get("https://api.open-meteo.com/v1/forecast?latitude=49.2827&longitude=-123.1207&current_weather=true").json()
            weather = f"{round(res['current_weather']['temperature'])}°C"
        except:
            weather = "Unknown"
            
        transit_data = await TransitService.get_next_buses(STOP_ID)
        calendar_data = CalendarService.get_upcoming_events()
        
        advice = AIService.get_commute_advice(
            transit_data = transit_data,
            calendar_data = calendar_data,
            user_question = "Give me a very short, punchy summary of my morning commute to UBC today. Make it SMS friendly.",
            weather_data = weather,
            direction = "UBC"
        )
        
        send_sms(advice)
    
    asyncio.run(generate_and_send())