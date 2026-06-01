# Grafana Cloud Setup (Free Tier)

## 1. Sign up
https://grafana.com/auth/sign-up — use your GitHub account

## 2. Create a stack
- Choose free tier
- Region: eu-west (London)
- Note your stack name e.g. `finsight-123456`

## 3. Get credentials
Go to: Home → Connections → Data sources → Prometheus → Connection

You'll get:
- Remote write URL: `https://prometheus-prod-XX-prod-eu-west-X.grafana.net/api/prom/push`
- Username: (numeric ID)
- Password: (API token — generate one)

Repeat for Loki connection.

## 4. Update prometheus.yml
Uncomment the `remote_write` block in `observability/prometheus/prometheus.yml`:

```yaml
remote_write:
  - url: YOUR_GRAFANA_PROM_URL
    basic_auth:
      username: YOUR_USERNAME
      password: YOUR_API_KEY
```

## 5. Update promtail config for Loki
In `observability/loki/promtail-config.yml`, change clients url:

```yaml
clients:
  - url: https://YOUR_LOKI_URL/loki/api/v1/push
    basic_auth:
      username: YOUR_LOKI_USERNAME
      password: YOUR_API_KEY
```

## 6. For production (k3s)
Store credentials as GitHub Secrets:
- `GRAFANA_PROM_URL`
- `GRAFANA_PROM_USER`
- `GRAFANA_API_KEY`
- `GRAFANA_LOKI_URL`
- `GRAFANA_LOKI_USER`

## 7. Import dashboard
In Grafana Cloud → Dashboards → Import
Use ID: `3662` (FastAPI Prometheus dashboard) as a starting point.
Then customize with FinSight panels.
