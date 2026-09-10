import math, time
import numpy as np
import sentry_sdk
from datetime import date
from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.responses import Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from sqlalchemy import select
from sqlalchemy.orm import Session
from .cache import cache
from .config import settings
from .db import Base, engine, get_db
from .market_data import fetch_yfinance, upsert_prices
from .metrics import CACHE_HITS, CACHE_MISSES, LATENCY, REQUESTS
from .models import Price
from .schemas import AnalyticsOut, IngestRequest, PriceOut

if settings.sentry_dsn:
    sentry_sdk.init(dsn=settings.sentry_dsn, environment=settings.app_env, traces_sample_rate=0.2)

Base.metadata.create_all(bind=engine)
app = FastAPI(title="Fund Analytics API", version="1.0.0")

@app.middleware("http")
async def observe(request: Request, call_next):
    started=time.perf_counter(); status=500
    try:
        response=await call_next(request); status=response.status_code; return response
    except Exception as exc:
        sentry_sdk.capture_exception(exc); raise
    finally:
        path=request.url.path
        REQUESTS.labels(request.method,path,str(status)).inc()
        LATENCY.labels(request.method,path).observe(time.perf_counter()-started)

@app.get("/health")
def health(): return {"status":"ok","environment":settings.app_env}

@app.get("/metrics")
def metrics(): return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.post("/ingest")
def ingest(req: IngestRequest, db: Session=Depends(get_db)):
    try: rows=fetch_yfinance(req.symbol, req.period)
    except Exception as e: raise HTTPException(400, str(e))
    added=upsert_prices(db, req.symbol.upper(), req.exchange.upper(), rows)
    cache.delete_prefix(f"prices:{req.symbol.upper()}:")
    cache.delete_prefix(f"analytics:{req.symbol.upper()}:")
    return {"symbol":req.symbol.upper(),"fetched":len(rows),"inserted":added}

@app.get("/prices/{symbol}", response_model=list[PriceOut])
def prices(symbol: str, start: date|None=None, end: date|None=None, limit: int=Query(1000,le=5000), db: Session=Depends(get_db)):
    symbol=symbol.upper(); key=f"prices:{symbol}:{start}:{end}:{limit}"
    cached=cache.get_json(key)
    if cached is not None:
        CACHE_HITS.labels("prices").inc(); return cached
    CACHE_MISSES.labels("prices").inc()
    q=select(Price).where(Price.symbol==symbol)
    if start: q=q.where(Price.trade_date>=start)
    if end: q=q.where(Price.trade_date<=end)
    rows=db.scalars(q.order_by(Price.trade_date).limit(limit)).all()
    out=[PriceOut.model_validate(r).model_dump(mode="json") for r in rows]
    cache.set_json(key,out); return out

@app.get("/analytics/{symbol}", response_model=AnalyticsOut)
def analytics(symbol: str, db: Session=Depends(get_db)):
    symbol=symbol.upper(); key=f"analytics:{symbol}:v1"
    cached=cache.get_json(key)
    if cached is not None:
        CACHE_HITS.labels("analytics").inc(); return cached
    CACHE_MISSES.labels("analytics").inc()
    rows=db.scalars(select(Price).where(Price.symbol==symbol).order_by(Price.trade_date)).all()
    if len(rows)<2: raise HTTPException(404,"Need at least two price points. Call /ingest first.")
    closes=np.array([r.close for r in rows],dtype=float)
    returns=np.diff(closes)/closes[:-1]
    running_max=np.maximum.accumulate(closes)
    dd=closes/running_max-1
    result={
      "symbol":symbol,"points":len(closes),"first_close":round(float(closes[0]),4),"last_close":round(float(closes[-1]),4),
      "total_return_pct":round(float((closes[-1]/closes[0]-1)*100),4),
      "annualized_volatility_pct":round(float(np.std(returns,ddof=1)*math.sqrt(252)*100),4) if len(returns)>1 else 0.0,
      "max_drawdown_pct":round(float(dd.min()*100),4)
    }
    cache.set_json(key,result); return result
