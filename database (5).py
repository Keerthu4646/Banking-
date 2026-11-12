import os
from sqlmodel import SQLModel, create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://bank:bank_password@postgres:5432/bank")
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

def get_session():
    with SessionLocal() as session:
        yield session

def create_tables():
    SQLModel.metadata.create_all(engine)
