from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from app.config import Config


@dataclass
class QueueItem:
    index: int
    node_operator_id: int
    count: int


class CsmService:
    def __init__(self, cfg: Config, adapter: Any) -> None:
        self.cfg = cfg
        self.adapter = adapter
        if not cfg.csm_address:
            raise RuntimeError(
                "COMMUNITY_STAKING_MODULE_ADDRESS is not set. Provide the CSM contract address."
            )
        self._contract = adapter.contract(cfg.csm_address, cfg.csm_abi)

    @staticmethod
    def _decode_batch(packed: int) -> Tuple[int, int]:
        """Decode packed Batch (uint256) into (nodeOperatorId, keysCount).

        Layout (from project spec):
          - uint64  nodeOperatorId (bits 192..255)
          - uint64  keysCount      (bits 128..191)
          - uint128 next           (bits 0..127)  -- ignored here
        """
        # Extract high 128 bits that contain id and count
        hi128 = int(packed >> 128)
        node_operator_id = int(hi128 >> 64) & ((1 << 64) - 1)
        count = int(hi128 & ((1 << 64) - 1))
        return node_operator_id, count

    def get_queue(self) -> Dict[str, Any]:
        head, tail = self._contract.functions.depositQueue().call()
        head_i = int(head)
        tail_i = int(tail)
        items: List[QueueItem] = []
        for i in range(head_i, tail_i):
            packed = int(self._contract.functions.depositQueueItem(i).call())
            no_id, cnt = self._decode_batch(packed)
            items.append(QueueItem(index=i, node_operator_id=no_id, count=cnt))
        return {
            "head": head_i,
            "tail": tail_i,
            "size": max(0, tail_i - head_i),
            "items": [item.__dict__ for item in items],
        }

    def list_node_operators(self) -> List[Dict[str, Any]]:
        """List node operators with key counts and status flags.

        Returns dicts with keys: id, deposited_keys, depositable_keys, enqueued_keys, is_active.
        """
        count = int(self._contract.functions.getNodeOperatorsCount().call())
        ids: List[int] = []
        # Fetch in a single call if small; otherwise page by 500
        if count <= 500:
            ids = list(map(int, self._contract.functions.getNodeOperatorIds(0, count).call()))
        else:
            off = 0
            while off < count:
                lim = min(500, count - off)
                batch = self._contract.functions.getNodeOperatorIds(off, lim).call()
                ids.extend(map(int, batch))
                off += lim

        items: List[Dict[str, Any]] = []
        for node_id in ids:
            # Prefer compact summary from getNodeOperator (struct with depositable and deposited keys)
            try:
                info = self._contract.functions.getNodeOperator(node_id).call()
                # info layout per ABI
                deposited = int(info[2])
                depositable = int(info[5])
                enqueued = int(info[9])
            except Exception:
                # Fallback to summary view if layout differs
                s = self._contract.functions.getNodeOperatorSummary(node_id).call()
                deposited = int(s[6])
                depositable = int(s[7])
                enqueued = 0
            # Active flag if available
            try:
                is_active = bool(self._contract.functions.getNodeOperatorIsActive(node_id).call())
            except Exception:
                is_active = None

            items.append(
                {
                    "id": int(node_id),
                    "deposited_keys": deposited,
                    "depositable_keys": depositable,
                    "enqueued_keys": enqueued,
                    "is_active": is_active,
                }
            )
        return items

    @staticmethod
    def _compute_positions(queue_items: List[Dict[str, Any]]) -> Dict[int, Dict[str, int]]:
        """Compute queue position metrics per node operator.

        For each node operator id, returns first occurrence index, total queued keys, and
        the number of keys ahead of their first batch (position_keys_ahead).
        """
        pos: Dict[int, Dict[str, int]] = {}
        ahead = 0
        for item in queue_items:
            idx = int(item["index"]) if "index" in item else int(item.get("idx", 0))
            no_id = int(item["node_operator_id"])
            cnt = int(item["count"])
            entry = pos.get(no_id)
            if entry is None:
                pos[no_id] = {
                    "first_queue_index": idx,
                    "queued_keys_total": cnt,
                    "position_keys_ahead": ahead,
                }
            else:
                entry["queued_keys_total"] += cnt
            ahead += cnt
        return pos

    def snapshot(self) -> Dict[str, Any]:
        """Return combined state: queue, node operators enriched with positions in queue."""
        queue = self.get_queue()
        operators = self.list_node_operators()
        positions = self._compute_positions(queue["items"]) if queue.get("items") else {}
        enriched_ops: List[Dict[str, Any]] = []
        for op in operators:
            pos = positions.get(int(op["id"]))
            if pos:
                op = {**op, **pos}
            enriched_ops.append(op)
        return {
            "queue": queue,
            "node_operators": enriched_ops,
        }


def make_csm_service(cfg: Config | None = None) -> CsmService:
    cfg = cfg or __import__("app.config", fromlist=["load_config"]).load_config()
    from web3 import Web3  # type: ignore
    from app.eth.adapter import EthAdapter  # type: ignore

    web3 = Web3(Web3.HTTPProvider(cfg.eth_rpc_url, request_kwargs={"timeout": cfg.eth_rpc_timeout}))
    adapter = EthAdapter(web3)
    return CsmService(cfg, adapter)
