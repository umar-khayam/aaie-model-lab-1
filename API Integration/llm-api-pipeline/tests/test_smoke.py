import asyncio, json
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def sample_payload():
    return {
        "domain": "Accounting",
        "prompt": "Analyze the impact of blockchain technology...",
        "rubric": {
            "rubric_id": "rub_accounting_0001",
            "criteria": [
                {"criterion_id":"c1","name":"Understanding","description":"..."},
                {"criterion_id":"c2","name":"Analysis","description":"..."}
            ]
        },
        "submission": "Sample student submission text...",
        "actual_label": "Human"
    }

def test_endpoints():
    for ep in ["classification", "confidence", "rubric-scores", "feedback", "evaluate"]:
        resp = client.post(f"/api/v1/{ep}", json=sample_payload())
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert isinstance(data, dict)
