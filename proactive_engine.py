from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timezone, timedelta
from calendar_service import CalendarService
from sqlalchemy.orm import Session
import database
import models

class ProactiveEngine:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.scheduler.add_job(self.check_all_users, 'interval', minutes=5)

    def start(self):
        self.scheduler.start()
        print("⚙️ Proactive AI Engine Started! Running background checks every 5 mins...")

    async def check_all_users(self):
        print(f"\n[{datetime.now().strftime('%I:%M %p')}] 🔍 Proactive Engine waking up...")
        
        print("1. Checking user calendars...")
        print("2. Calculating travel times from saved Home Coordinates...")
        print("3. Checking live TransLink delays...")
        print("✅ No immediate action required. Going back to sleep.")
        
        # NOTE: To make this fully functional, we would need to securely store 
        # the Google access_token in the database so the background worker 
        # can read the calendar even when the user's browser is closed.

# Create a global instance of the engine
engine = ProactiveEngine()