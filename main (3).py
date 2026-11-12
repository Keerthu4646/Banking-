import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, Header
from sqlmodel import Session, select
from app.database import get_session, create_tables
from app.models import Notification
from app.security import get_current_user

INTERNAL_TOKEN = os.getenv("INTERNAL_TOKEN", "change-this-internal-token")

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables(); yield

app = FastAPI(title="Notification Service", lifespan=lifespan)

@app.get("/health")
def health(): return {"status":"ok"}

@app.get("/")
def list_notifications(current_user: dict = Depends(get_current_user), session: Session = Depends(get_session)):
    return session.exec(select(Notification).where(Notification.user_id == current_user["user_id"]).order_by(Notification.id.desc())).all()

@app.post("/internal")
def create_notification(payload: dict, x_internal_token: str = Header(), session: Session = Depends(get_session)):
    if x_internal_token != INTERNAL_TOKEN: raise HTTPException(403, "Forbidden")
    notification = Notification(user_id=payload["user_id"], title=payload["title"], message=payload["message"])
    session.add(notification); session.commit(); session.refresh(notification)
    return notification
