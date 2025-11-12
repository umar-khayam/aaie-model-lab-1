import json, os
from typing import Any, Dict

def load_json(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def ensure_dir(p: str) -> None:
    os.makedirs(p, exist_ok=True)
