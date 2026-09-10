-- Run after ingesting enough data. PostgreSQL only.
EXPLAIN (ANALYZE, BUFFERS) SELECT * FROM prices WHERE symbol='RELIANCE.NS' ORDER BY trade_date DESC LIMIT 1000;
EXPLAIN (ANALYZE, BUFFERS) SELECT avg(close) FROM prices WHERE symbol='RELIANCE.NS' AND trade_date >= CURRENT_DATE - INTERVAL '365 days';
EXPLAIN (ANALYZE, BUFFERS) SELECT symbol, max(close), min(close) FROM prices GROUP BY symbol;
EXPLAIN (ANALYZE, BUFFERS) SELECT * FROM prices WHERE exchange='NSE' AND symbol='RELIANCE.NS' AND trade_date BETWEEN CURRENT_DATE - INTERVAL '180 days' AND CURRENT_DATE;
