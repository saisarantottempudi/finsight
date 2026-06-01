# FinSight — Real-time Portfolio Risk & Fraud Analytics Platform

End-to-end fintech platform with ML-powered fraud detection, quantitative risk metrics, and full DevOps stack. Built for portfolio demonstration of Data Engineering, MLOps, and Cloud DevOps skills.

## Architecture

```
GitHub Actions (CI/CD)
    │
    ▼ build + push
ghcr.io (container registry)
    │
    ▼ deploy
Oracle Cloud ARM k3s cluster
├── FastAPI (Risk API + Fraud Detection)
├── Streamlit (Dashboard)
├── Data Ingestion (yfinance → PostgreSQL)
└── Prometheus + Promtail
    │                 │
    ▼                 ▼
Neon.tech        Grafana Cloud
(PostgreSQL)     (Metrics + Logs + Traces)
```

## Features

- **Portfolio Risk Analytics**: VaR (95%/99%), Sharpe ratio, annualized volatility, max drawdown
- **Fraud Detection**: IsolationForest ML model scoring every transaction in real-time
- **Market Data Ingestion**: Async pipeline fetching live prices (yfinance) into TimescaleDB-compatible PostgreSQL
- **Full Observability**: Metrics (Prometheus), logs (Loki), traces (OpenTelemetry/Jaeger)
- **Zero Cost**: Runs entirely on free tiers — Oracle Cloud, Neon, Grafana Cloud, GitHub

## Tech Stack

| Layer | Technology |
|---|---|
| API | FastAPI + Python 3.12 |
| Database | PostgreSQL (Neon.tech free tier) |
| ML | scikit-learn IsolationForest |
| Dashboard | Streamlit + Plotly |
| Containers | Docker (multi-stage builds) |
| Orchestration | Kubernetes (k3s on Oracle Cloud ARM) |
| IaC | Terraform (Oracle Cloud provider) |
| CI/CD | GitHub Actions |
| Registry | GitHub Container Registry (ghcr.io) |
| Metrics | Prometheus → Grafana Cloud |
| Logs | Promtail → Grafana Cloud Loki |
| Traces | OpenTelemetry → Grafana Cloud Tempo |
| Auth | JWT (python-jose) |
| Secrets | GitHub Secrets + Doppler |

## Quick Start (Local)

```bash
cp .env.example .env
make up          # starts all services via Docker Compose
make migrate     # runs Alembic migrations
make obs-up      # starts observability stack (optional)
```

Services:
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Dashboard: http://localhost:8501
- Grafana: http://localhost:3000 (local only)
- Prometheus: http://localhost:9090 (local only)
- Jaeger: http://localhost:16686 (local only)

## Running Tests

```bash
make test
```

## Deployment

See `infra/` for Terraform (Oracle Cloud) and Helm chart (k3s).

## Cost

**$0/month** — all services on permanent free tiers.

---

*Built by [Tottempudi Sai Saran](https://linkedin.com/in/tottempudi-sai-saran) | [GitHub](https://github.com/saisarantottempudi)*
