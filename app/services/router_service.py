from __future__ import annotations

from dataclasses import asdict
from typing import List

from app.config import Config
from app.models import Module


class RouterService:
    def __init__(self, cfg: Config, adapter: EthAdapter) -> None:
        self.cfg = cfg
        self.adapter = adapter

    def _resolve_router_address(self) -> str:
        if self.cfg.staking_router_address:
            return self.cfg.staking_router_address
        if not self.cfg.lido_locator_address:
            raise RuntimeError(
                "No STAKING_ROUTER_ADDRESS provided and LIDO_LOCATOR_ADDRESS is missing."
            )
        return self.adapter.resolve_staking_router(self.cfg.lido_locator_address, self.cfg.locator_abi)

    def list_modules(self) -> List[Module]:
        router_address = self._resolve_router_address()
        # Will raise NotImplementedError until ABI is provided and enumerator implemented.
        raw = self.adapter.list_modules(router_address, self.cfg.router_abi)
        return [
            Module(
                address=item.get("address", "0x0"),
                module_id=item.get("id"),
                name=item.get("name"),
                module_type=item.get("type"),
                target_share_bps=item.get("target_share_bps"),
                is_active=item.get("is_active"),
                is_deposits_paused=item.get("is_deposits_paused"),
                is_stopped=item.get("is_stopped"),
                active_validators=item.get("active_validators"),
                depositable_validators=item.get("depositable_validators"),
                last_deposit_block=item.get("last_deposit_block"),
                max_deposits_per_block=item.get("max_deposits_per_block"),
                min_deposit_block_distance=item.get("min_deposit_block_distance"),
            )
            for item in raw
        ]

    @staticmethod
    def serialize(modules: List[Module]) -> List[dict]:
        return [asdict(m) for m in modules]


def make_router_service(cfg: Config | None = None) -> RouterService:
    cfg = cfg or __import__("app.config", fromlist=["load_config"]).load_config()
    # Lazy imports to avoid hard dependency during tests that stub the service
    from web3 import Web3  # type: ignore
    from app.eth.adapter import EthAdapter  # type: ignore

    web3 = Web3(Web3.HTTPProvider(cfg.eth_rpc_url, request_kwargs={"timeout": cfg.eth_rpc_timeout}))
    adapter = EthAdapter(web3)
    return RouterService(cfg, adapter)
