import os, random
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, Header
from sqlmodel import Session, select
from app.database import get_session, create_tables
from app.models import Account
from app.security import get_current_user

INTERNAL_TOKEN = os.getenv("INTERNAL_TOKEN", "change-this-internal-token")

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables(); yield

app = FastAPI(title="Account Service", lifespan=lifespan)

def require_internal(x_internal_token: str = Header()):
    if x_internal_token != INTERNAL_TOKEN: raise HTTPException(403, "Forbidden")

def get_account(account_id:int, session:Session, user_id:int):
    account = session.get(Account, account_id)
    if not account or account.user_id != user_id: raise HTTPException(404, "Account not found")
    return account

@app.get("/health")
def health(): return {"status":"ok"}

@app.post("/")
def create_account(current_user: dict = Depends(get_current_user), session: Session = Depends(get_session)):
    account = Account(user_id=current_user["user_id"], account_number="AC"+"".join(random.choices("0123456789", k=10)))
    session.add(account); session.commit(); session.refresh(account)
    return account

@app.get("/")
def list_accounts(current_user: dict = Depends(get_current_user), session: Session = Depends(get_session)):
    return session.exec(select(Account).where(Account.user_id == current_user["user_id"])).all()

@app.get("/{account_id}")
def get_balance(account_id:int, current_user: dict = Depends(get_current_user), session: Session = Depends(get_session)):
    return get_account(account_id, session, current_user["user_id"])

@app.post("/internal/{account_id}/debit")
def debit(account_id:int, amount:float, x_internal_token:str = Header(), session:Session=Depends(get_session)):
    require_internal(x_internal_token)
    account = session.get(Account, account_id)
    if not account: raise HTTPException(404, "Account not found")
    if account.balance < amount: raise HTTPException(400, "Insufficient funds")
    account.balance -= amount; session.add(account); session.commit()
    return {"account_id":account.id,"balance":account.balance}

@app.post("/internal/{account_id}/credit")
def credit(account_id:int, amount:float, x_internal_token:str = Header(), session:Session=Depends(get_session)):
    require_internal(x_internal_token)
    account = session.get(Account, account_id)
    if not account: raise HTTPException(404, "Account not found")
    account.balance += amount; session.add(account); session.commit()
    return {"account_id":account.id,"balance":account.balance}
