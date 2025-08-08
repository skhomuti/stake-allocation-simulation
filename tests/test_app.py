from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_healthz_ok():
    resp = client.get("/healthz")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_index_ok():
    resp = client.get("/")
    assert resp.status_code == 200
    # Basic smoke check that the template rendered
    assert "Welcome" in resp.text or "Stake Allocation Simulation" in resp.text

