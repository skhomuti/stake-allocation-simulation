
import pytest

from app.config import load_config
from app.eth.adapter import EthAdapter

integration = pytest.mark.integration


@integration
def test_live_adapter_resolve_and_modules():
    cfg = load_config()
    from web3 import Web3  # import locally to avoid hard dependency during collection
    web3 = Web3(Web3.HTTPProvider(cfg.eth_rpc_url, request_kwargs={"timeout": 15}))
    adapter = EthAdapter(web3)

    # Resolve router via locator if not provided explicitly
    router_addr = cfg.staking_router_address
    if not router_addr and cfg.lido_locator_address:
        router_addr = adapter.resolve_staking_router(cfg.lido_locator_address, cfg.locator_abi)

    assert router_addr and router_addr.startswith("0x") and len(router_addr) == 42

    modules = adapter.list_modules(router_addr, cfg.router_abi)
    assert isinstance(modules, list)
    # Addresses should be valid format
    assert all(m.get("address", "").startswith("0x") and len(m["address"]) == 42 for m in modules)
