from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Config:
    eth_rpc_url: str
    eth_rpc_timeout: int = 20
    # Prefer locator; if provided and router not set, we will resolve via locator.
    lido_locator_address: Optional[str] = None
    staking_router_address: Optional[str] = None
    # ABI file names under `abi/`
    locator_abi: str = "locator.json"
    router_abi: str = "staking_router.json"
    # Community Staking Module (CSM)
    csm_address: Optional[str] = None
    csm_abi: str = "csm.json"


def load_config() -> Config:
    rpc = os.getenv("ETH_RPC_URL", "")
    timeout = int(os.getenv("ETH_RPC_TIMEOUT", "20"))
    locator = os.getenv("LIDO_LOCATOR_ADDRESS")
    router = os.getenv("STAKING_ROUTER_ADDRESS")
    locator_abi = os.getenv("LOCATOR_ABI", "locator.json")
    router_abi = os.getenv("ROUTER_ABI", "staking_router.json")
    csm_address = os.getenv("COMMUNITY_STAKING_MODULE_ADDRESS")
    csm_abi = os.getenv("CSM_ABI", "csm.json")

    return Config(
        eth_rpc_url=rpc,
        eth_rpc_timeout=timeout,
        lido_locator_address=locator,
        staking_router_address=router,
        locator_abi=locator_abi,
        router_abi=router_abi,
        csm_address=csm_address,
        csm_abi=csm_abi,
    )
