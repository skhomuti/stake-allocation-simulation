from typing import Any, Dict, List

from app.config import Config
from app.models import Module
from app.services.router_service import RouterService


class _StubAdapter:
    def __init__(self, items: List[Dict[str, Any]]):
        self._items = items

    def list_modules(self, router_address: str, router_abi: str) -> List[Dict[str, Any]]:  # noqa: D401
        return self._items

    def resolve_staking_router(self, locator_address: str, locator_abi: str) -> str:
        return "0x0000000000000000000000000000000000000000"


def test_router_service_mapping_full_fields():
    cfg = Config(
        eth_rpc_url="http://localhost",
        staking_router_address="0x0000000000000000000000000000000000000000",
    )
    raw = [
        {
            "id": 1,
            "address": "0x1111111111111111111111111111111111111111",
            "name": "Curated",
            "type": "curated",
            "target_share_bps": 4200,
            "is_active": True,
            "is_deposits_paused": False,
            "is_stopped": False,
            "active_validators": 1000,
            "last_deposit_block": 123,
            "max_deposits_per_block": 30,
            "min_deposit_block_distance": 1,
        }
    ]
    service = RouterService(cfg, _StubAdapter(raw))
    modules = service.list_modules()
    assert len(modules) == 1
    m: Module = modules[0]
    assert m.module_id == 1
    assert m.address.startswith("0x1111")
    assert m.name == "Curated"
    assert m.module_type == "curated"
    assert m.target_share_bps == 4200
    assert m.is_active is True
    assert m.is_deposits_paused is False
    assert m.is_stopped is False
    assert m.active_validators == 1000
    assert m.last_deposit_block == 123
    assert m.max_deposits_per_block == 30
    assert m.min_deposit_block_distance == 1

