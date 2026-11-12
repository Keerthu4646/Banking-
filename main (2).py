from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from passlib.context import CryptContext
from app.database import get_session, create_tables
from app.models import User
from app.security import create_token, get_current_user

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables(); yield

app = FastAPI(title="Auth Service", lifespan=lifespan)

@app.get("/health")
def health(): return {"status":"ok"}

@app.post("/register")
def register(email: str, full_name: str, password: str, session: Session = Depends(get_session)):
    if session.exec(select(User).where(User.email == email)).first():
        raise HTTPException(400, "Email already registered")
    user = User(email=email, full_name=full_name, hashed_password=pwd.hash(password))
    session.add(user); session.commit(); session.refresh(user)
    return {"id": user.id, "email": user.email}

@app.post("/login")
def login(form: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.email == form.username)).first()
    if not user or not pwd.verify(form.password, user.hashed_password):
        raise HTTPException(401, "Invalid credentials")
    return {"access_token": create_token(user.id, user.email), "token_type":"bearer",
            "user":{"id":user.id,"email":user.email,"full_name":user.full_name}}

@app.get("/me")
def me(current_user: dict = Depends(get_current_user)):
    return current_user
