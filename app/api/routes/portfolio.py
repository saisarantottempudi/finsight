import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Portfolio
from app.db.session import get_db
from app.schemas.portfolio import PortfolioCreate, PortfolioResponse

router = APIRouter()


@router.post("/", response_model=PortfolioResponse, status_code=201)
async def create_portfolio(payload: PortfolioCreate, db: AsyncSession = Depends(get_db)):
    portfolio = Portfolio(id=uuid.uuid4(), user_id=payload.user_id, name=payload.name)
    db.add(portfolio)
    await db.commit()
    await db.refresh(portfolio)
    return portfolio


@router.get("/{portfolio_id}", response_model=PortfolioResponse)
async def get_portfolio(portfolio_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Portfolio).where(Portfolio.id == portfolio_id))
    portfolio = result.scalar_one_or_none()
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    return portfolio


@router.get("/user/{user_id}", response_model=list[PortfolioResponse])
async def list_portfolios(user_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Portfolio).where(Portfolio.user_id == user_id))
    return result.scalars().all()
