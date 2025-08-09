from __future__ import annotations

import json
import os
from typing import Any, Dict


def load_abi_file(filename: str) -> Dict[str, Any]:
    """Load an ABI JSON from `abi/<filename>`.

    Raises FileNotFoundError with a clear message if missing.
    """
    path = os.path.join("abi", filename)
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"ABI file not found: {path}. Please add it (see README for instructions)."
        )
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

