from datetime import datetime, timezone
from sqlmodel import SQLModel, Field

class Account(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(index=True)
    account_number: str = Field(unique=True)
    balance: float = 0.0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
