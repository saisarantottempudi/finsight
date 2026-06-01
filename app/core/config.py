from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://finsight:finsight@localhost:5432/finsight"
    SECRET_KEY: str = "changeme"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    MARKET_DATA_SYMBOLS: list[str] = ["AAPL", "GOOGL", "MSFT", "JPM", "GS"]
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    OTEL_ENDPOINT: str = "http://jaeger:4317"
    MODEL_PATH: str = "/models/fraud_detector.pkl"

    class Config:
        env_file = ".env"


settings = Settings()
