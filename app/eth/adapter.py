from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import logging

from app.eth.abi_loader import load_abi_file


logger = logging.getLogger(__name__)


@dataclass
class EthAdapter:
    web3: Any

    def contract(self, address: str, abi_filename: str) -> Any:
        abi = load_abi_file(abi_filename)
        return self.web3.eth.contract(address=self.web3.to_checksum_address(address), abi=abi)

    def resolve_staking_router(self, locator_address: str, locator_abi: str) -> str:
        """Resolve the StakingRouter address via the Lido Locator contract.

        Expects the locator ABI to include a `stakingRouter()` view that returns `address`.
        If your ABI differs, adjust the ABI or extend this method.
        """
        locator = self.contract(locator_address, locator_abi)
        try:
            return locator.functions.stakingRouter().call()
        except Exception as exc:  # pragma: no cover - depends on real ABI
            raise RuntimeError(
                "Failed to resolve staking router via locator. Ensure the locator ABI"
                " exposes a `stakingRouter()` view or update EthAdapter.resolve_staking_router()."
            ) from exc

    def list_modules(self, router_address: str, router_abi: str) -> List[Dict[str, Any]]:
        """Return staking modules with best-effort enrichment.

        Tries in order:
        1) getAllStakingModuleDigests() + per-id flag/counter getters
        2) Enumerate ids (getStakingModuleIds/getStakingModulesCount) + per-id getters
        3) Fallback to getStakingModules() returning only addresses
        """
        router = self.contract(router_address, router_abi)

        # 0) Preferred: try `getAllStakingModuleDigests()` which returns rich info including
        #    name, share limits, and some timing/block params. We additionally enrich each
        #    digest with status flags and counters via per-id getters to provide a complete
        #    module snapshot expected by the service/tests.
        try:
            digests = router.functions.getAllStakingModuleDigests().call()
            modules: List[Dict[str, Any]] = []
            for d in digests or []:
                # Each digest has fields: nodeOperatorsCount, activeNodeOperatorsCount, state, summary
                state = None
                if isinstance(d, (list, tuple)) and len(d) >= 3:
                    state = d[2]
                elif isinstance(d, dict):
                    state = d.get("state")
                if not state:
                    continue
                # State is a struct; try to access by index and by key
                def _get(s, key, idx):
                    if isinstance(s, dict):
                        return s.get(key)
                    if isinstance(s, (list, tuple)) and len(s) > idx:
                        return s[idx]
                    return None

                mid = _get(state, "id", 0)
                maddr = _get(state, "stakingModuleAddress", 1)
                fee = _get(state, "stakingModuleFee", 2)
                treasury_fee = _get(state, "treasuryFee", 3)
                share_limit = _get(state, "stakeShareLimit", 4)
                status = _get(state, "status", 5)
                name = _get(state, "name", 6)
                last_deposit_at = _get(state, "lastDepositAt", 7)
                last_deposit_block = _get(state, "lastDepositBlock", 8)
                exited_count = _get(state, "exitedValidatorsCount", 9)
                priority_exit_threshold = _get(state, "priorityExitShareThreshold", 10)
                max_per_block = _get(state, "maxDepositsPerBlock", 11)
                min_block_distance = _get(state, "minDepositBlockDistance", 12)

                if isinstance(maddr, str) and maddr.startswith("0x"):
                    mid_int = int(mid) if mid is not None else None

                    # Enrich with flags/counters not present directly in digest
                    is_active: Optional[bool] = None
                    is_deposits_paused: Optional[bool] = None
                    is_stopped: Optional[bool] = None
                    active_validators: Optional[int] = None
                    if mid_int is not None:
                        try:
                            is_active = bool(router.functions.getStakingModuleIsActive(mid_int).call())
                        except Exception:
                            logger.debug("getStakingModuleIsActive(%s) failed", mid_int, exc_info=True)
                        try:
                            is_deposits_paused = bool(
                                router.functions.getStakingModuleIsDepositsPaused(mid_int).call()
                            )
                        except Exception:
                            logger.debug(
                                "getStakingModuleIsDepositsPaused(%s) failed", mid_int, exc_info=True
                            )
                        try:
                            is_stopped = bool(router.functions.getStakingModuleIsStopped(mid_int).call())
                        except Exception:
                            logger.debug("getStakingModuleIsStopped(%s) failed", mid_int, exc_info=True)
                        try:
                            active_validators = int(
                                router.functions.getStakingModuleActiveValidatorsCount(mid_int).call()
                            )
                        except Exception:
                            logger.debug(
                                "getStakingModuleActiveValidatorsCount(%s) failed", mid_int, exc_info=True
                            )

                    modules.append(
                        {
                            "id": mid_int,
                            "address": self.web3.to_checksum_address(maddr),
                            "name": name if isinstance(name, str) else None,
                            "target_share_bps": int(share_limit) if share_limit is not None else None,
                            "last_deposit_block": int(last_deposit_block) if last_deposit_block is not None else None,
                            "max_deposits_per_block": int(max_per_block) if max_per_block is not None else None,
                            "min_deposit_block_distance": int(min_block_distance) if min_block_distance is not None else None,
                            "is_active": is_active,
                            "is_deposits_paused": is_deposits_paused,
                            "is_stopped": is_stopped,
                            "active_validators": active_validators,
                        }
                    )
            if modules:
                return modules
        except Exception:
            logger.debug("getAllStakingModuleDigests() unavailable or failed; falling back", exc_info=True)
