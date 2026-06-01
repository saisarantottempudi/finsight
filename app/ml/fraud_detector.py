import os

import joblib
import numpy as np
import structlog
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

from app.core.config import settings

log = structlog.get_logger()


class FraudDetector:
    def __init__(self):
        self.model = IsolationForest(n_estimators=100, contamination=0.05, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False

    def _features(self, t: dict) -> list[float]:
        return [
            t["quantity"],
            t["price"],
            t["quantity"] * t["price"],
            t.get("hour_of_day", 12),
            1.0 if t["transaction_type"] == "BUY" else -1.0,
        ]

    def train(self, transactions: list[dict]) -> None:
        X = np.array([self._features(t) for t in transactions])
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled)
        self.is_trained = True
        self._save()
        log.info("fraud_model_trained", n_samples=len(transactions))

    def predict(self, transaction: dict) -> dict:
        if not self.is_trained:
            self._load()
        X = np.array([self._features(transaction)])
        X_scaled = self.scaler.transform(X)
        score = float(self.model.score_samples(X_scaled)[0])
        prediction = int(self.model.predict(X_scaled)[0])
        label = "fraud" if prediction == -1 else "clean"
        return {"label": label, "anomaly_score": round(score, 4), "is_suspicious": prediction == -1}

    def _save(self) -> None:
        os.makedirs(os.path.dirname(settings.MODEL_PATH), exist_ok=True)
        joblib.dump({"model": self.model, "scaler": self.scaler}, settings.MODEL_PATH)

    def _load(self) -> None:
        if os.path.exists(settings.MODEL_PATH):
            data = joblib.load(settings.MODEL_PATH)
            self.model = data["model"]
            self.scaler = data["scaler"]
            self.is_trained = True
        else:
            self._bootstrap_train()

    def _bootstrap_train(self) -> None:
        """Train on synthetic normal data so the model is always available."""
        rng = np.random.default_rng(42)
        transactions = [
            {
                "quantity": float(rng.uniform(1, 100)),
                "price": float(rng.uniform(10, 500)),
                "transaction_type": "BUY" if rng.random() > 0.5 else "SELL",
                "hour_of_day": int(rng.integers(9, 17)),
            }
            for _ in range(200)
        ]
        self.train(transactions)
        log.info("fraud_model_bootstrapped_with_synthetic_data")


fraud_detector = FraudDetector()
