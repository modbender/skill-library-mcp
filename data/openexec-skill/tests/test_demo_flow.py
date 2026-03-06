import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from main import app
from openexec.db import init_db

init_db()

client = TestClient(app)

def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"

def test_version():
    resp = client.get("/version")
    assert resp.status_code == 200
    data = resp.json()
    assert "version" in data

def test_ready():
    resp = client.get("/ready")
    assert resp.status_code == 200
    assert resp.json()["ready"] is True

def test_execute_echo():
    resp = client.post("/execute", json={
        "action": "echo",
        "payload": {"msg": "hello"},
        "nonce": "test-nonce-1"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["action"] == "echo"
    assert data["result"]["echo"]["msg"] == "hello"
    assert data["approved"] is True
    assert "receipt" in data

def test_replay_protection():
    resp1 = client.post("/execute", json={
        "action": "add",
        "payload": {"a": 2, "b": 3},
        "nonce": "test-nonce-2"
    })
    resp2 = client.post("/execute", json={
        "action": "add",
        "payload": {"a": 2, "b": 3},
        "nonce": "test-nonce-2"
    })
    assert resp1.json()["id"] == resp2.json()["id"]

def test_receipt_verification():
    from openexec.receipts import verify_receipt
    import json
    resp = client.post("/execute", json={
        "action": "add",
        "payload": {"a": 10, "b": 20},
        "nonce": "test-nonce-3"
    })
    data = resp.json()
    result_str = json.dumps(data["result"], sort_keys=True)
    assert verify_receipt(data["id"], result_str, data["receipt"])
