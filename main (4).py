import os
from collections import defaultdict
from contextlib import asynccontextmanager
import httpx
from fastapi import FastAPI, Depends
from app.security import get_current_user

TRANSACTION_SERVICE_URL = os.getenv("TRANSACTION_SERVICE_URL", "http://transaction-service:8000")

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

app = FastAPI(title="Reporting Service", lifespan=lifespan)
client = httpx.AsyncClient(timeout=10.0)

@app.get("/health")
def health(): return {"status":"ok"}

@app.get("/summary")
async def summary(current_user: dict = Depends(get_current_user)):
    response = await client.get(f"{TRANSACTION_SERVICE_URL}/", headers={"Authorization": f"Bearer {current_user.get('token','')}"})
    response.raise_for_status()
    transactions = response.json()
    totals = defaultdict(float)
    for t in transactions: totals[t["status"]] += t["amount"]
    return {"user_id":current_user["user_id"], "transaction_count":len(transactions), "total_by_status":dict(totals)}
