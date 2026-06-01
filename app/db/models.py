import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Enum, Float, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class TransactionType(enum.Enum):
    BUY = "BUY"
    SELL = "SELL"


class FraudLabel(enum.Enum):
    clean = "clean"
    suspicious = "suspicious"
    fraud = "fraud"


class Portfolio(Base):
    __tablename__ = "portfolios"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String, nullable=False, index=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    transactions = relationship("Transaction", back_populates="portfolio", lazy="select")


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    portfolio_id = Column(UUID(as_uuid=True), ForeignKey("portfolios.id"), nullable=False)
    symbol = Column(String(10), nullable=False)
    quantity = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    transaction_type = Column(Enum(TransactionType), nullable=False)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    is_flagged = Column(String, default="clean")
    anomaly_score = Column(Float, nullable=True)

    portfolio = relationship("Portfolio", back_populates="transactions")

    __table_args__ = (Index("idx_transactions_symbol_ts", "symbol", "timestamp"),)


class MarketPrice(Base):
    __tablename__ = "market_prices"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    symbol = Column(String(10), nullable=False)
    price = Column(Float, nullable=False)
    open = Column(Float, nullable=True)
    high = Column(Float, nullable=True)
    low = Column(Float, nullable=True)
    volume = Column(Float, nullable=True)
    timestamp = Column(DateTime(timezone=True), nullable=False)

    __table_args__ = (Index("idx_market_symbol_ts", "symbol", "timestamp"),)
