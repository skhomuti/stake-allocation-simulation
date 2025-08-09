import pytest
import web3

from app.config import Config
from app.services.router_service import make_router_service, RouterService


def test_make_router_service_uses_real_web3():
    cfg = Config(
        eth_rpc_url="http://example",
        eth_rpc_timeout=13,
        staking_router_address="0x0000000000000000000000000000000000000000",
    )

    service = make_router_service(cfg)
    assert isinstance(service, RouterService)
    assert service.cfg is cfg

    # Verify real Web3 was constructed with our provider and timeout
    assert isinstance(service.adapter.web3, web3.Web3)  # type: ignore[attr-defined]
    provider = service.adapter.web3.provider  # type: ignore[attr-defined]
    assert getattr(provider, "endpoint_uri", None) == "http://example"
    # request_kwargs may be attached to underlying HTTP session; check attribute if present
    timeout = getattr(provider, "_request_kwargs", {}).get("timeout") or getattr(provider, "request_kwargs", {}).get("timeout")
    assert timeout == 13
