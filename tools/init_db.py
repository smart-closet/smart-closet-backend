import os
from sqlalchemy import create_engine
from sqlmodel import SQLModel

def init_db():
    DATABASE_URL = os.getenv("DATABASE_URL")
    engine = create_engine(DATABASE_URL)

    SQLModel.metadata.create_all(engine)
    SQLModel.metadata.drop_all(engine)


if __name__ == "__main__":
    init_db()