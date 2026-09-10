import time
from prometheus_client import Counter, Histogram

REQUESTS = Counter("fund_api_requests_total", "Total HTTP requests", ["method", "path", "status"])
LATENCY = Histogram("fund_api_request_latency_seconds", "Request latency", ["method", "path"])
CACHE_HITS = Counter("fund_api_cache_hits_total", "Cache hits", ["endpoint"])
CACHE_MISSES = Counter("fund_api_cache_misses_total", "Cache misses", ["endpoint"])
