from datetime import date
import yfinance as yf
from sqlalchemy.orm import Session
from .models import Price


def fetch_yfinance(symbol: str, period: str = "5y"):
    df = yf.download(symbol, period=period, auto_adjust=False, progress=False)
    if df.empty:
        raise ValueError(f"No market data returned for {symbol}")
    if getattr(df.columns, "nlevels", 1) > 1:
        df.columns = df.columns.get_level_values(0)
    rows=[]
    for idx, row in df.iterrows():
        rows.append({
            "trade_date": idx.date(), "open": float(row["Open"]), "high": float(row["High"]),
            "low": float(row["Low"]), "close": float(row["Close"]), "volume": float(row.get("Volume",0) or 0)
        })
    return rows


def upsert_prices(db: Session, symbol: str, exchange: str, rows: list[dict]) -> int:
    # Portable ORM implementation; unique constraint prevents duplicate dates.
    existing = {row[0] for row in db.query(Price.trade_date).filter(Price.symbol==symbol, Price.exchange==exchange).all()}
    added=0
    for row in rows:
        d=row["trade_date"]
        if d in existing: continue
        db.add(Price(symbol=symbol, exchange=exchange, **row)); added += 1
    db.commit()
    return added
