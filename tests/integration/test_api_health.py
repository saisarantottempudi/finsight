import os
import sys

import pytest
from httpx import ASGITransport, AsyncClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../app"))

os.environ["DATABASE_URL"] = "postgresql+asyncpg://finsight:finsight@localhost:5432/finsight"
os.environ["SECRET_KEY"] = "test-secret"
os.environ["MODEL_PATH"] = "/tmp/test_model.pkl"


@pytest.mark.anyio
async def test_health_endpoint():
    from main import app

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        r = await client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "healthy"
    assert r.json()["service"] == "finsight-api"


@pytest.mark.anyio
async def test_docs_available():
    from main import app

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        r = await client.get("/docs")
    assert r.status_code == 200
