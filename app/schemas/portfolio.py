from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class PortfolioCreate(BaseModel):
    user_id: str
    name: str


class PortfolioResponse(BaseModel):
    id: UUID
    user_id: str
    name: str
    created_at: datetime

    class Config:
        from_attributes = True
