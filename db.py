from sqlmodel import create_engine, Session
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

def get_session():
    with Session(engine) as session:
        yield session

# SQLModel.metadata.drop_all(engine)
# SQLModel.metadata.create_all(engine)