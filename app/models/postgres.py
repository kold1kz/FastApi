from sqlalchemy import create_engine, Column, String, Integer, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from .models  import *
from databases import Database




SQLALCHEMY_DATABASE_URL = "postgresql://hamm:1234@localhost:5432/FastApi"


engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

database = Database(SQLALCHEMY_DATABASE_URL)




def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# def get_postgres(db = Depends(postgres.get_db)):
#     return (db.query(models.Item).all())