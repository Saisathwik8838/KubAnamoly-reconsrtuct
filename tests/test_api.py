"""
Integration tests for FastAPI Center Endpoints (Table VI in Paper)
"""
from pathlib import Path
import json
try:
    import pytest
except ImportError:
    pytest = None

from analyzer.app.main import app
from analyzer.app.services.feature_extractor import extract_features, FEATURES

def test_feature_extraction_fixture():
    fixture_path = Path(__file__).resolve().parent / "fixtures" / "sample_falco_events.json"
    assert fixture_path.exists()
    records = json.loads(fixture_path.read_text(encoding="utf-8"))
    
    res = extract_features(records, container_id="a1b2c3d4e5f6")
    assert len(res["feature_vector"]) == 36
    assert res["feature_names"] == FEATURES
    assert res["mapped_event_count"] >= 3
    # Check that openat on /etc/passwd increments 'etc' directory count
    assert res["feature_counts"]["etc"] >= 1
    # Check that connect increments connect and network_connection
    assert res["feature_counts"]["connect"] >= 1
    assert res["feature_counts"]["network_connection"] >= 1

def test_health_endpoint():
    from fastapi.testclient import TestClient
    client = TestClient(app)
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert "models_available" in data

def test_hardware_endpoints():
    from fastapi.testclient import TestClient
    client = TestClient(app)
    payload = {
        "metrics": [{"container": "alpine_test", "cpu_percent": "0.1%", "memory_percent": "0.5%"}],
        "collected_at": "2026-11-17T12:00:00Z"
    }
    post_resp = client.post("/hardware", json=payload)
    assert post_resp.status_code == 200
    assert post_resp.json()["containers_received"] == 1

    get_resp = client.get("/hardware/latest")
    assert get_resp.status_code == 200
    assert get_resp.json()["status"] == "success"

def test_scheduler_endpoints():
    from fastapi.testclient import TestClient
    client = TestClient(app)
    status_resp = client.get("/scheduler/status")
    assert status_resp.status_code == 200
    assert status_resp.json()["status"] == "success"
