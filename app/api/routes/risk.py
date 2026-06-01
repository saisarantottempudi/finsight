import pandas as pd
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import MarketPrice, Transaction
from app.db.session import get_db
from app.ml.risk_engine import RiskEngine
from app.schemas.risk import RiskMetricsResponse

router = APIRouter()
risk_engine = RiskEngine()


@router.get("/{portfolio_id}", response_model=RiskMetricsResponse)
async def get_risk_metrics(portfolio_id: str, db: AsyncSession = Depends(get_db)):
    txn_result = await db.execute(
        select(Transaction).where(Transaction.portfolio_id == portfolio_id)
    )
    transactions = txn_result.scalars().all()
    if not transactions:
        raise HTTPException(status_code=404, detail="No transactions found for this portfolio")

    weights: dict[str, float] = {}
    for t in transactions:
        delta = t.quantity * t.price if t.transaction_type.value == "BUY" else -(t.quantity * t.price)
        weights[t.symbol] = weights.get(t.symbol, 0.0) + delta

    weights = {k: v for k, v in weights.items() if v > 0}
    if not weights:
        raise HTTPException(status_code=400, detail="No positive holdings in portfolio")

    symbols = list(weights.keys())
    price_result = await db.execute(
        select(MarketPrice)
        .where(MarketPrice.symbol.in_(symbols))
        .order_by(MarketPrice.timestamp)
    )
    prices_data = price_result.scalars().all()
    if not prices_data:
        raise HTTPException(status_code=404, detail="No market price data available")

    df = pd.DataFrame(
        [{"symbol": p.symbol, "price": p.price, "ts": p.timestamp} for p in prices_data]
    )
    price_pivot = df.pivot_table(index="ts", columns="symbol", values="price").ffill()

    if len(price_pivot) < 2:
        raise HTTPException(status_code=400, detail="Insufficient price history for risk calculation")

    metrics = risk_engine.compute(price_pivot, weights)
    return RiskMetricsResponse(
        portfolio_value=metrics.portfolio_value,
        daily_volatility=metrics.daily_volatility,
        annualized_volatility=metrics.annualized_volatility,
        sharpe_ratio=metrics.sharpe_ratio,
        var_95=metrics.var_95,
        var_99=metrics.var_99,
        max_drawdown=metrics.max_drawdown,
    )
