from datetime import date
from pydantic import BaseModel, Field

class PriceOut(BaseModel):
    symbol: str
    exchange: str
    trade_date: date
    open: float
    high: float
    low: float
    close: float
    volume: float
    model_config = {"from_attributes": True}

class AnalyticsOut(BaseModel):
    symbol: str
    points: int
    first_close: float
    last_close: float
    total_return_pct: float
    annualized_volatility_pct: float
    max_drawdown_pct: float

class IngestRequest(BaseModel):
    symbol: str = Field(min_length=1, max_length=32, examples=["RELIANCE.NS"])
    period: str = "5y"
    exchange: str = "NSE"
