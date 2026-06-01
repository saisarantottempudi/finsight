import asyncio
import os
from datetime import datetime, timezone

import asyncpg
import structlog
import yfinance as yf

log = structlog.get_logger()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://finsight:finsight@localhost:5432/finsight")
SYMBOLS = os.getenv("SYMBOLS", "AAPL,GOOGL,MSFT,JPM,GS").split(",")
INTERVAL_SECONDS = int(os.getenv("INTERVAL_SECONDS", "60"))


async def fetch_and_store(conn: asyncpg.Connection) -> None:
    for symbol in SYMBOLS:
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.fast_info
            price = getattr(info, "last_price", None)
            if price is None:
                log.warning("no_price", symbol=symbol)
                continue

            hist = ticker.history(period="1d", interval="1m")
            open_ = float(hist["Open"].iloc[0]) if not hist.empty else None
            high = float(hist["High"].max()) if not hist.empty else None
            low = float(hist["Low"].min()) if not hist.empty else None
            volume = float(hist["Volume"].sum()) if not hist.empty else None

            await conn.execute(
                """
                INSERT INTO market_prices (id, symbol, price, open, high, low, volume, timestamp)
                VALUES (gen_random_uuid(), $1, $2, $3, $4, $5, $6, $7)
                """,
                symbol,
                float(price),
                open_,
                high,
                low,
                volume,
                datetime.now(timezone.utc),
            )
            log.info("price_stored", symbol=symbol, price=price)
        except Exception as e:
            log.error("fetch_error", symbol=symbol, error=str(e))


async def main() -> None:
    log.info("ingestion_started", symbols=SYMBOLS, interval_seconds=INTERVAL_SECONDS)
    conn = None
    while True:
        try:
            if conn is None or conn.is_closed():
                conn = await asyncpg.connect(DATABASE_URL)
            await fetch_and_store(conn)
        except Exception as e:
            log.error("ingestion_loop_error", error=str(e))
            conn = None
        await asyncio.sleep(INTERVAL_SECONDS)


if __name__ == "__main__":
    asyncio.run(main())
