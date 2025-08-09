import pytest
from fastapi.testclient import TestClient

from app.main import app


integration = pytest.mark.integration


@integration
def test_live_api_modules():
    client = TestClient(app)
    resp = client.get("/api/modules", timeout=30)
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    if data:
        assert data[0]["address"].startswith("0x")
