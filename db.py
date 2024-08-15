from sqlmodel import create_engine, Session, SQLModel
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

def get_session():
    with Session(engine) as session:
        yield session

def create_tables():
    SQLModel.metadata.create_all(engine)

def drop_tables():
    SQLModel.metadata.drop_all(engine)