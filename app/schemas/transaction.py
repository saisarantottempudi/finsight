from pydantic import BaseModel, field_validator
from uuid import UUID
from datetime import datetime
from typing import Literal


class TransactionCreate(BaseModel):
    portfolio_id: UUID
    symbol: str
    quantity: float
    price: float
    transaction_type: Literal["BUY", "SELL"]

    @field_validator("quantity", "price")
    @classmethod
    def must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("must be positive")
        return v

    @field_validator("symbol")
    @classmethod
    def symbol_uppercase(cls, v):
        return v.upper().strip()


class TransactionResponse(BaseModel):
    id: UUID
    portfolio_id: UUID
    symbol: str
    quantity: float
    price: float
    transaction_type: str
    timestamp: datetime
    is_flagged: str
    anomaly_score: float | None

    class Config:
        from_attributes = True
