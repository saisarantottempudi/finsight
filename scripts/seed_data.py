"""
Seed script — creates a test portfolio and sample transactions to demo the platform.
Run: python scripts/seed_data.py
Requires API running at localhost:8000
"""
import httpx
import json

API = "http://localhost:8000"


def main():
    print("Seeding FinSight with demo data...")

    # Create portfolio
    r = httpx.post(f"{API}/api/v1/portfolio/", json={"user_id": "demo-user", "name": "Demo Portfolio"})
    r.raise_for_status()
    portfolio = r.json()
    pid = portfolio["id"]
    print(f"Created portfolio: {pid}")

    # Normal transactions
    normal_txns = [
        {"portfolio_id": pid, "symbol": "AAPL", "quantity": 10, "price": 185.50, "transaction_type": "BUY"},
        {"portfolio_id": pid, "symbol": "GOOGL", "quantity": 5, "price": 175.20, "transaction_type": "BUY"},
        {"portfolio_id": pid, "symbol": "MSFT", "quantity": 8, "price": 420.00, "transaction_type": "BUY"},
        {"portfolio_id": pid, "symbol": "JPM", "quantity": 15, "price": 198.30, "transaction_type": "BUY"},
        {"portfolio_id": pid, "symbol": "GS", "quantity": 3, "price": 485.00, "transaction_type": "BUY"},
        {"portfolio_id": pid, "symbol": "AAPL", "quantity": 2, "price": 188.00, "transaction_type": "SELL"},
    ]

    # Suspicious transaction (large notional, unusual price)
    suspicious = {"portfolio_id": pid, "symbol": "AAPL", "quantity": 50000, "price": 9999.99, "transaction_type": "BUY"}

    for txn in normal_txns:
        r = httpx.post(f"{API}/api/v1/transactions/", json=txn)
        result = r.json()
        print(f"  {txn['symbol']} {txn['transaction_type']}: {result['fraud_assessment']['label']} "
              f"(score: {result['fraud_assessment']['anomaly_score']})")

    print("\nAdding suspicious transaction...")
    r = httpx.post(f"{API}/api/v1/transactions/", json=suspicious)
    result = r.json()
    print(f"  AAPL BUY (50000 @ $9999): {result['fraud_assessment']['label']} "
          f"(score: {result['fraud_assessment']['anomaly_score']})")

    print(f"\nDone! Portfolio ID: {pid}")
    print(f"View dashboard: http://localhost:8501")
    print(f"API docs: http://localhost:8000/docs")
    print(f"Risk metrics: http://localhost:8000/api/v1/risk/{pid}")


if __name__ == "__main__":
    main()
