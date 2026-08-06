import sys
import os
sys.path.append(os.path.dirname(__file__))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

try:
    print("Testing GET /api/stocks/RELIANCE.NS...")
    res = client.get("/api/stocks/RELIANCE.NS")
    data = res.json()
    print("SUCCESS: Symbol:", data['symbol'], "Candles count:", len(data['candles']))
    print("Latest:", data['latest'])
except Exception as e:
    import traceback
    print("ERROR:")
    traceback.print_exc()
