from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Service Imports
from transit_service import TransitService
from ai_service import AIService
from calendar_service import CalendarService # Only importing the correct web version!
from geo_service import GeoService
from proactive_engine import engine
import database
import models

@asynccontextmanager
async def lifespan(app: FastAPI):
    database.init_db()
    print("✅ Database tables created/verified!")
    
    engine.start()
    
    yield 
    
    print("💤 Proactive Engine shutting down...")


app = FastAPI(title="Transit & Task Optimizer", lifespan=lifespan)

class LoginRequest(BaseModel):
    email: str
    name: str

class SettingsRequest(BaseModel):
    email: str
    home_address: str
    school_address: str

class CalendarSyncRequest(BaseModel):
    email: str
    access_token: str
    
class ChatRequest(BaseModel):
    email: str
    question: str
    weather: str
    direction: str
    events: list = [] 

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "Online", "message": "Transit Optimizer API is running"}

@app.get("/test-db")
def test_db(db: Session = Depends(database.get_db)):
    user_count = db.query(models.User).count()
    return {"message": "Connection successful", "user_count": user_count}

@app.get("/transit/{stop_id}")
async def get_transit_estimates(stop_id: str):
    data = await TransitService.get_next_buses(stop_id)
    return data

@app.post("/chat")
async def chat_with_assistant(
    request: ChatRequest, 
    db: Session = Depends(database.get_db)
):
    user = db.query(models.User).filter(models.User.email == request.email).first()
    if not user:
        return {"reply": "User profile not found. Please refresh and log in again."}

    active_stop_id = user.ubc_stop_id if request.direction == "UBC" else user.home_stop_id

    live_transit_data = await TransitService.get_next_buses(active_stop_id)
    upcoming_schedule = request.events
    
    ai_response = AIService.get_commute_advice(
        transit_data=live_transit_data,
        calendar_data=upcoming_schedule, 
        user_question=request.question,
        weather_data=request.weather,
        direction=request.direction
    )
    
    new_log = models.CommuteLog(
        user_email=request.email,
        stop_id=active_stop_id,
        direction=request.direction,
        weather_temp=request.weather,
        user_question=request.question,
        ai_recommendation=ai_response
    )
    db.add(new_log)  
    db.commit()      
    
    return {"reply": ai_response}

@app.post("/login")
def login_user(request: LoginRequest, db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.email == request.email).first()
    
    if not user:
        user = models.User(email=request.email, name=request.name)
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"🌟 NEW USER REGISTERED: {user.name}")
    else:
        print(f"👋 WELCOME BACK: {user.name}")
        
    return {"status": "success", "home_stop": user.home_stop_id, "ubc_stop": user.ubc_stop_id}

@app.post("/update-settings")
async def update_settings(
    request: SettingsRequest, 
    db: Session = Depends(database.get_db)
):
    user = db.query(models.User).filter(models.User.email == request.email).first()
    if not user:
        return {"error": "User not found"}

    user.home_address = request.home_address
    user.school_address = request.school_address

    home_coords = await GeoService.get_coordinates(request.home_address)
    school_coords = await GeoService.get_coordinates(request.school_address)

    if home_coords[0]:
        user.home_lat, user.home_lon = home_coords
    if school_coords[0]:
        user.school_lat, user.school_lon = school_coords

    db.commit()
    print(f"📍 Location locked for {user.name}: Home({user.home_lat}, {user.home_lon})")
    
    return {"message": "Spatial coordinates locked in!"}

@app.post("/sync-calendar")
async def sync_calendar(request: CalendarSyncRequest):
    print(f"📅 Syncing calendar for {request.email}...")
    
    events = await CalendarService.get_upcoming_events(request.access_token)
    
    if not events:
        return {"message": "No upcoming events found or token invalid."}
        
    print(f"✅ Found {len(events)} upcoming events!")
    for e in events:
        print(f" - {e['title']} at {e['start']}")
        
    return {"message": "Calendar synced successfully!", "events": events}