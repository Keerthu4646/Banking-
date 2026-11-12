import enum
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field

class TransactionStatus(str, enum.Enum):
    pending="PENDING"; completed="COMPLETED"; failed="FAILED"

class Transaction(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(index=True)
    from_account_id: int
    to_account_id: int
    amount: float
    status: TransactionStatus = TransactionStatus.pending
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
