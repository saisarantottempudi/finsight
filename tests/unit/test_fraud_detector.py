import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../app"))

os.environ["MODEL_PATH"] = "/tmp/test_fraud_model.pkl"
os.environ["DATABASE_URL"] = "postgresql+asyncpg://x:x@localhost/x"
os.environ["SECRET_KEY"] = "test"

from ml.fraud_detector import FraudDetector


@pytest.fixture
def trained_detector(tmp_path):
    os.environ["MODEL_PATH"] = str(tmp_path / "model.pkl")
    detector = FraudDetector()
    normal = [
        {"quantity": float(i % 50 + 1), "price": 150.0, "transaction_type": "BUY", "hour_of_day": 10}
        for i in range(200)
    ]
    detector.train(normal)
    return detector


def test_normal_transaction_clean(trained_detector):
    result = trained_detector.predict(
        {"quantity": 10, "price": 150.0, "transaction_type": "BUY", "hour_of_day": 10}
    )
    assert result["label"] == "clean"
    assert "anomaly_score" in result
    assert isinstance(result["anomaly_score"], float)


def test_anomalous_transaction_flagged(trained_detector):
    result = trained_detector.predict(
        {"quantity": 999999, "price": 999999.0, "transaction_type": "BUY", "hour_of_day": 3}
    )
    assert result["label"] == "fraud"
    assert result["is_suspicious"] is True


def test_prediction_returns_required_keys(trained_detector):
    result = trained_detector.predict(
        {"quantity": 5, "price": 100.0, "transaction_type": "SELL", "hour_of_day": 14}
    )
    assert {"label", "anomaly_score", "is_suspicious"} == set(result.keys())
