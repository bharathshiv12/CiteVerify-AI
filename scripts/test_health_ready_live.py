import sys
sys.path.insert(0, "backend")

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
res = client.get("/api/health/ready")
print("Status code:", res.status_code)
print("Response JSON:", res.json())
