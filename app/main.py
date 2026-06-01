from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from app.api.routes import health, portfolio, transactions, risk
from app.core.config import settings
from app.core.telemetry import setup_telemetry

app = FastAPI(
    title="FinSight API",
    description="Real-time Portfolio Risk & Fraud Analytics",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

Instrumentator().instrument(app).expose(app)
setup_telemetry(app)

app.include_router(health.router, tags=["health"])
app.include_router(portfolio.router, prefix="/api/v1/portfolio", tags=["portfolio"])
app.include_router(transactions.router, prefix="/api/v1/transactions", tags=["transactions"])
app.include_router(risk.router, prefix="/api/v1/risk", tags=["risk"])
