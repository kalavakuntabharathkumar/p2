import json
from redis import Redis
from .config import settings

class Cache:
    def __init__(self):
        self._memory = {}
        self.client = None
        try:
            self.client = Redis.from_url(settings.redis_url, decode_responses=True, socket_connect_timeout=0.3)
            self.client.ping()
        except Exception:
            self.client = None

    def get_json(self, key: str):
        raw = self.client.get(key) if self.client else self._memory.get(key)
        return json.loads(raw) if raw else None

    def set_json(self, key: str, value, ttl: int | None = None):
        raw = json.dumps(value, default=str)
        if self.client:
            self.client.setex(key, ttl or settings.cache_ttl_seconds, raw)
        else:
            self._memory[key] = raw

    def delete_prefix(self, prefix: str):
        if self.client:
            for key in self.client.scan_iter(f"{prefix}*"):
                self.client.delete(key)
        else:
            for key in list(self._memory):
                if key.startswith(prefix): self._memory.pop(key, None)

cache = Cache()
