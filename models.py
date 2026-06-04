# from datetime import datetime
# from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
# from sqlalchemy.orm import declarative_base, relationship
# from database import Base
# from sqlalchemy.sql import func

# Base = declarative_base()

# class User(Base):
#     __tablename__ = "users"

#     id = Column(Integer, primary_key=True, index=True)
#     email = Column(String, unique=True, index=True)
#     name = Column(String)
    
#     home_stop_id = Column(String, default="s-c2b2j3t111-eastboundw49ave~balsamst") 
#     ubc_stop_id = Column(String, default="s-c2b2j9x0c8-westboundw49ave~wiltshirest")

# class LocationNode(Base):
#     __tablename__ = 'location_nodes'

#     id = Column(Integer, primary_key=True, index=True)
#     user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
#     label = Column(String, nullable=False)
#     latitude = Column(Float, nullable=False)
#     longitude = Column(Float, nullable=False)
#     is_default_origin = Column(Boolean, default=False)

#     user = relationship("User", back_populates="locations")
#     events = relationship("FixedEvent", back_populates="location")


# class FixedEvent(Base):
#     __tablename__ = 'fixed_events'

#     id = Column(Integer, primary_key=True, index=True)
#     user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
#     location_id = Column(Integer, ForeignKey('location_nodes.id'), nullable=True)
    
#     title = Column(String, nullable=False)
#     start_time = Column(DateTime, nullable=False)
#     end_time = Column(DateTime, nullable=False)
#     provider = Column(String, nullable=False) 
#     external_event_id = Column(String, nullable=True)
#     user = relationship("User", back_populates="fixed_events")
#     location = relationship("LocationNode", back_populates="events")


# class FlexibleTask(Base):
#     __tablename__ = 'flexible_tasks'

#     id = Column(Integer, primary_key=True, index=True)
#     user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
#     title = Column(String, nullable=False)
#     duration_minutes = Column(Integer, nullable=False) 
#     priority = Column(String, default="Medium")
#     is_completed = Column(Boolean, default=False)
#     deadline = Column(DateTime, nullable=True)

#     user = relationship("User", back_populates="flexible_tasks")


# class CalendarSyncToken(Base):
#     __tablename__ = 'calendar_sync_tokens'

#     id = Column(Integer, primary_key=True, index=True)
#     user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
#     provider = Column(String, nullable=False)
#     access_token = Column(String, nullable=False)
#     refresh_token = Column(String, nullable=True)
#     expires_at = Column(DateTime, nullable=False)

#     user = relationship("User", back_populates="sync_tokens")
    
# class CommuteLog(Base):
#     __tablename__ = "commute_logs"

#     id = Column(Integer, primary_key=True, index=True)
#     timestamp = Column(DateTime, default=func.now())
    
#     user_email = Column(String, index=True)
    
#     stop_id = Column(String, index=True)
#     direction = Column(String)
#     weather_temp = Column(String)
#     user_question = Column(String)
#     ai_recommendation = Column(String)

from sqlalchemy import Column, Integer, String, DateTime, Float
from sqlalchemy.sql import func
from database import Base

# class User(Base):
#     __tablename__ = "users"

#     id = Column(Integer, primary_key=True, index=True)
#     email = Column(String, unique=True, index=True)
#     name = Column(String)
    
#     home_stop_id = Column(String, default="s-c2b2j3t111-eastboundw49ave~balsamst") 
#     ubc_stop_id = Column(String, default="s-c2b2j9x0c8-westboundw49ave~wiltshirest")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String)
    
    # The Legacy Stop IDs (Needed for the Chat feature)
    home_stop_id = Column(String, default="s-c2b2j3t111-eastboundw49ave~balsamst") 
    ubc_stop_id = Column(String, default="s-c2b2j9x0c8-westboundw49ave~wiltshirest")

    # New Spatial Awareness Columns (Needed for the Proactive AI)
    home_address = Column(String, nullable=True)
    home_lat = Column(Float, nullable=True)
    home_lon = Column(Float, nullable=True)
    
    school_address = Column(String, nullable=True)
    school_lat = Column(Float, nullable=True)
    school_lon = Column(Float, nullable=True)

class CommuteLog(Base):
    __tablename__ = "commute_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=func.now())
    
    user_email = Column(String, index=True) 
    stop_id = Column(String, index=True)
    direction = Column(String)
    weather_temp = Column(String)
    user_question = Column(String)
    ai_recommendation = Column(String)