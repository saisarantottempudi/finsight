import uuid
from datetime import datetime, timezone

import structlog
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Transaction, TransactionType
from app.db.session import get_db
from app.ml.fraud_detector import fraud_detector
from app.schemas.transaction import TransactionCreate, TransactionResponse

log = structlog.get_logger()
router = APIRouter()


@router.post("/", status_code=201)
async def create_transaction(payload: TransactionCreate, db: AsyncSession = Depends(get_db)):
    now = datetime.now(timezone.utc)
    fraud_result = fraud_detector.predict(
        {
            "quantity": payload.quantity,
            "price": payload.price,
            "transaction_type": payload.transaction_type,
            "hour_of_day": now.hour,
        }
    )

    txn = Transaction(
        id=uuid.uuid4(),
        portfolio_id=payload.portfolio_id,
        symbol=payload.symbol,
        quantity=payload.quantity,
        price=payload.price,
        transaction_type=TransactionType[payload.transaction_type],
        timestamp=now,
        is_flagged=fraud_result["label"],
        anomaly_score=fraud_result["anomaly_score"],
    )
    db.add(txn)
    await db.commit()
    await db.refresh(txn)

    log.info(
        "transaction_created",
        txn_id=str(txn.id),
        symbol=txn.symbol,
        fraud_label=fraud_result["label"],
        anomaly_score=fraud_result["anomaly_score"],
    )

    return {
        "transaction_id": str(txn.id),
        "symbol": txn.symbol,
        "fraud_assessment": fraud_result,
    }


@router.get("/portfolio/{portfolio_id}", response_model=list[TransactionResponse])
async def list_transactions(portfolio_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Transaction)
        .where(Transaction.portfolio_id == portfolio_id)
        .order_by(Transaction.timestamp.desc())
    )
    return result.scalars().all()


@router.get("/flagged/{portfolio_id}", response_model=list[TransactionResponse])
async def get_flagged(portfolio_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Transaction)
        .where(
            Transaction.portfolio_id == portfolio_id,
            Transaction.is_flagged != "clean",
        )
        .order_by(Transaction.timestamp.desc())
    )
    flagged = result.scalars().all()
    if not flagged:
        raise HTTPException(status_code=404, detail="No flagged transactions found")
    return flagged
