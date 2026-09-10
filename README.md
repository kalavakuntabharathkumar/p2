# Fund Analytics API Performance & Monitoring Platform

FastAPI + PostgreSQL + Redis project for ingesting real historical equity data, serving price/analytics endpoints, load testing, query profiling, Prometheus metrics, and optional Sentry monitoring.

## Run quickly

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # Windows: copy .env.example .env
# For zero-config local use, set DATABASE_URL=sqlite:///./fund_analytics.db in .env
uvicorn app.main:app --reload
```

Open `http://localhost:8000/docs`. Ingest a real symbol with `POST /ingest`, e.g. `{ "symbol": "RELIANCE.NS", "period": "5y", "exchange": "NSE" }`.

## PostgreSQL + Redis

```bash
cp .env.example .env
docker compose up --build
```

## Performance workflow

1. Ingest one or more NSE/BSE Yahoo Finance symbols (e.g. `RELIANCE.NS`, `TCS.NS`, `500325.BO`).
2. Run `scripts/explain_queries.sql` in PostgreSQL to inspect plans and index usage.
3. Start API, then run: `locust -f locustfile.py --host http://localhost:8000 --headless -u 25 -r 5 -n 1000`.
4. Compare first request vs cached requests and inspect `/metrics` in Prometheus/Grafana.

The resume numbers in the original project description are **benchmark targets/claims to reproduce**, not hard-coded results. Record your actual p95, query times, and error rates after running on your machine/data.

## Useful endpoints

- `GET /health`
- `POST /ingest`
- `GET /prices/{symbol}`
- `GET /analytics/{symbol}`
- `GET /metrics`

## Grafana/Prometheus
Prometheus-compatible metrics are exposed at `/metrics`. Add this API as a scrape target, then chart `fund_api_request_latency_seconds` and request counters in Grafana.
