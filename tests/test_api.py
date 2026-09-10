from fastapi.testclient import TestClient
from app.main import app
client=TestClient(app)
def test_health(): assert client.get('/health').status_code==200
def test_missing_analytics(): assert client.get('/analytics/NO_SUCH_SYMBOL').status_code==404
