import pytest

from app.config import load_config
from app.services.router_service import make_router_service


@pytest.mark.integration
def test_modules_fields_filled_from_rpc():
    cfg = load_config()
    service = make_router_service(cfg)
    modules = service.list_modules()

    assert isinstance(modules, list)
    assert len(modules) > 0, "Expected at least one staking module from router"

    # Verify that key fields are fully populated for each module
    # Note: module_type is optional and may be None depending on router ABI
    for m in modules:
        assert isinstance(m.address, str) and m.address.startswith("0x") and len(m.address) == 42
        assert m.module_id is not None
        assert m.name is not None and len(m.name) > 0
        assert m.target_share_bps is not None
        assert m.is_active is not None
        assert m.is_deposits_paused is not None
        assert m.is_stopped is not None
        assert m.active_validators is not None
        assert m.last_deposit_block is not None
        assert m.max_deposits_per_block is not None
        assert m.min_deposit_block_distance is not None
