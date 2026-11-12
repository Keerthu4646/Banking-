import os
from contextlib import asynccontextmanager
import httpx
from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import Session, select
from app.database import get_session, create_tables
from app.models import Transaction, TransactionStatus
from app.security import get_current_user

INTERNAL_TOKEN = os.getenv("INTERNAL_TOKEN", "change-this-internal-token")
ACCOUNT_SERVICE_URL = os.getenv("ACCOUNT_SERVICE_URL", "http://account-service:8000")
NOTIFICATION_SERVICE_URL = os.getenv("NOTIFICATION_SERVICE_URL", "http://notification-service:8000")

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables(); yield

app = FastAPI(title="Transaction Service", lifespan=lifespan)
client = httpx.AsyncClient(timeout=10.0)

@app.get("/health")
def health(): return {"status":"ok"}

@app.get("/")
async def list_transactions(current_user: dict = Depends(get_current_user), session: Session = Depends(get_session)):
    return session.exec(select(Transaction).where(Transaction.user_id == current_user["user_id"]).order_by(Transaction.id.desc())).all()

@app.post("/transfer")
async def transfer(from_account_id:int, to_account_id:int, amount:float,
                   current_user: dict = Depends(get_current_user), session: Session = Depends(get_session)):
    if amount <= 0: raise HTTPException(400, "Amount must be positive")
    if from_account_id == to_account_id: raise HTTPException(400, "Source and destination must differ")
    headers={"X-Internal-Token":INTERNAL_TOKEN}
    tx=Transaction(user_id=current_user["user_id"], from_account_id=from_account_id, to_account_id=to_account_id, amount=amount)
    session.add(tx); session.commit(); session.refresh(tx)
    try:
        (await client.post(f"{ACCOUNT_SERVICE_URL}/internal/{from_account_id}/debit", params={"amount":amount}, headers=headers)).raise_for_status()
        (await client.post(f"{ACCOUNT_SERVICE_URL}/internal/{to_account_id}/credit", params={"amount":amount}, headers=headers)).raise_for_status()
        tx.status=TransactionStatus.completed
    except Exception:
        tx.status=TransactionStatus.failed; session.add(tx); session.commit()
        raise HTTPException(502, "Transfer failed")
    session.add(tx); session.commit()
    try:
        await client.post(f"{NOTIFICATION_SERVICE_URL}/internal", json={"user_id":current_user["user_id"],"title":"Transfer completed","message":f"Transferred {amount} from {from_account_id} to {to_account_id}."}, headers=headers)
    except Exception: pass
    return tx
