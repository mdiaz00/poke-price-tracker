# database/db_init.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.models import Base

DATABASE_URL = "sqlite:///pokeprices.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()
    print("Database created successfully!")
