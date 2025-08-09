from __future__ import annotations

from functools import lru_cache

from app.config import load_config
from app.services.router_service import RouterService, make_router_service


@lru_cache(maxsize=1)
def get_router_service() -> RouterService:
    cfg = load_config()
    return make_router_service(cfg)

