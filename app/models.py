from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class Module:
    address: str
    module_id: Optional[int] = None
    name: Optional[str] = None
    module_type: Optional[str] = None
    # Allocation/weights
    target_share_bps: Optional[int] = None
    # Status flags
    is_active: Optional[bool] = None
    is_deposits_paused: Optional[bool] = None
    is_stopped: Optional[bool] = None
    # Operational metrics
    active_validators: Optional[int] = None
    # Validators that can be deposited right now (capacity)
    depositable_validators: Optional[int] = None
    last_deposit_block: Optional[int] = None
    max_deposits_per_block: Optional[int] = None
    min_deposit_block_distance: Optional[int] = None
