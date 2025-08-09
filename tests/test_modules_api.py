from dataclasses import dataclass
from typing import List

from fastapi.testclient import TestClient

from app.main import app
import app.deps as deps
from app.models import Module


@dataclass
class _StubService:
    def list_modules(self) -> List[Module]:
        return [
            Module(
                address="0x1111111111111111111111111111111111111111",
                module_id=1,
                name="Curated",
                module_type="curated",
                target_share_bps=5000,
                is_active=True,
                is_deposits_paused=False,
                is_stopped=False,
                active_validators=1234,
                last_deposit_block=18_765_432,
                max_deposits_per_block=30,
                min_deposit_block_distance=1,
            ),
            Module(
                address="0x2222222222222222222222222222222222222222",
                module_id=2,
                name="CSM",
                module_type="csm",
                target_share_bps=5000,
                is_active=False,
                is_deposits_paused=True,
                is_stopped=False,
                active_validators=567,
                last_deposit_block=18_765_400,
                max_deposits_per_block=15,
                min_deposit_block_distance=2,
            ),
        ]


def test_modules_endpoint_with_stub(monkeypatch):
    def _get_stub():
        return _StubService()  # type: ignore

    # Override FastAPI dependency
    app.dependency_overrides[deps.get_router_service] = _get_stub

    client = TestClient(app)
    resp = client.get("/api/modules")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) == 2
    assert data[0]["address"].startswith("0x1111")
    # Check enriched fields
    assert data[0]["is_active"] is True
    assert data[0]["is_deposits_paused"] is False
    assert data[0]["is_stopped"] is False
    assert data[0]["active_validators"] == 1234
    assert data[0]["last_deposit_block"] == 18765432
    assert data[0]["max_deposits_per_block"] == 30
    assert data[0]["min_deposit_block_distance"] == 1
    # Cleanup override
    app.dependency_overrides.clear()
