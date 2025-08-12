from dataclasses import dataclass
from fastapi.testclient import TestClient

from app.main import app
import app.deps as deps


@dataclass
class _StubCsmService:
    def snapshot(self):
        return {
            "queue": {
                "head": 10,
                "tail": 13,
                "size": 3,
                "items": [
                    {"index": 10, "node_operator_id": 1, "count": 2},
                    {"index": 11, "node_operator_id": 2, "count": 1},
                    {"index": 12, "node_operator_id": 1, "count": 3},
                ],
            },
            "node_operators": [
                {
                    "id": 1,
                    "deposited_keys": 5,
                    "depositable_keys": 7,
                    "enqueued_keys": 3,
                    "is_active": True,
                    "first_queue_index": 10,
                    "queued_keys_total": 5,
                    "position_keys_ahead": 0,
                },
                {
                    "id": 2,
                    "deposited_keys": 2,
                    "depositable_keys": 0,
                    "enqueued_keys": 1,
                    "is_active": False,
                    "first_queue_index": 11,
                    "queued_keys_total": 1,
                    "position_keys_ahead": 2,
                },
            ],
        }


def test_csm_state_endpoint_with_stub(monkeypatch):
    def _get_stub():
        return _StubCsmService()  # type: ignore

    app.dependency_overrides[deps.get_csm_service] = _get_stub
    client = TestClient(app)
    resp = client.get("/api/csm/state")
    assert resp.status_code == 200
    data = resp.json()
    assert "queue" in data and "node_operators" in data
    assert data["queue"]["size"] == 3
    assert isinstance(data["node_operators"], list)
    assert data["node_operators"][0]["id"] == 1
    # cleanup override
    app.dependency_overrides.clear()

