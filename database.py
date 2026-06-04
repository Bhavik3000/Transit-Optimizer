# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker
# from models import Base
# import urllib.parse

# password = urllib.parse.quote_plus("@iG3nwKb5TiqhYC0y")
# DATABASE_URL = "postgresql://postgres:iG3nwKb5TiqhYC0y@db.uauxyqygrqvyjdqqdlpj.supabase.co:5432/postgres"

# engine = create_engine(DATABASE_URL)

# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# def init_db():
#     Base.metadata.create_all(bind=engine)

# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

SQLALCHEMY_DATABASE_URL = "sqlite:///./transit.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def init_db():
    """Creates the tables in the database."""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Opens a database session for FastAPI and closes it when done."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()