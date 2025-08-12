from fastapi.testclient import TestClient

from app.main import app


def test_csm_page_renders():
    client = TestClient(app)
    resp = client.get("/csm")
    assert resp.status_code == 200
    assert "CSM Queue" in resp.text

