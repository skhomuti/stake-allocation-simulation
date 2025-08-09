from dataclasses import dataclass
from typing import Any, Dict, List

import builtins

from app.eth.adapter import EthAdapter


class _Call:
    def __init__(self, value):
        self._value = value

    def call(self):
        return self._value


class _StubFunctions:
    def __init__(self, handlers: Dict[str, Any]):
        self._h = handlers

    def __getattr__(self, name: str):
        fn = self._h.get(name)
        if fn is None:
            def _missing(*args, **kwargs):
                raise AttributeError(name)

            return _missing

        def _wrapper(*args, **kwargs):
            res = fn(*args, **kwargs) if callable(fn) else fn
            return _Call(res)

        return _wrapper


class _StubContract:
    def __init__(self, handlers: Dict[str, Any]):
        self.functions = _StubFunctions(handlers)


@dataclass
class _StubWeb3:
    def to_checksum_address(self, addr: str) -> str:
        # For testing, just return the input in lowercase as a deterministic transform
        return addr.lower()

    class eth:
        contract = None  # not used; we override adapter.contract in tests


def test_resolve_staking_router(monkeypatch):
    adapter = EthAdapter(_StubWeb3())

    def _contract(address: str, abi_filename: str):
        return _StubContract({
            "stakingRouter": lambda: "0xABCDEF",
        })

    monkeypatch.setattr(adapter, "contract", _contract)
    got = adapter.resolve_staking_router("0xLOCATOR", "locator.json")
    assert got == "0xABCDEF"
