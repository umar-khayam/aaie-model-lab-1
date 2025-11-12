import os, hashlib, collections
from typing import List, Dict, Any
from app.config import DATA_DIR, FEWSHOT_MAX
from app.utils.json_io import load_json

def _domain_filename(domain: str) -> str:
    alias = domain.strip().lower()
    mapping = {
        "accounting": "accounting.json",
        "manufacturing engineering": "engineering.json",
        "engineering": "engineering.json",
        "information technology": "it.json",
        "it": "it.json",
        "psychology": "psychology.json",
        "teaching": "teaching.json",
    }
    # Use os.path.normpath to get Windows-friendly backslashes
    return os.path.normpath(os.path.join(DATA_DIR, mapping.get(alias, f"{alias}.json")))

def load_domain_dataset(domain: str) -> Dict[str, Any]:
    path = _domain_filename(domain)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Domain file not found for '{domain}'. Expected at {path}")
    return load_json(path)

def _stable_hash(s: str) -> int:
    return int(hashlib.sha256(s.encode("utf-8")).hexdigest(), 16)

def fewshots_for_domain(domain: str, k: int = None) -> List[Dict[str, Any]]:
    ds = load_domain_dataset(domain)
    subs = ds.get("submissions", [])
    if not subs:
        return []

    if k is None:
        k = FEWSHOT_MAX

    buckets = collections.defaultdict(list)
    for ex in subs:
        buckets[ex.get("label_type", "Unknown")].append(ex)

    for label in buckets:
        buckets[label].sort(key=lambda x: _stable_hash(x.get("final_submission","")))

    order = ["AI", "Human", "Hybrid"]
    picks = []
    idx = 0
    while len(picks) < min(k, len(subs)):
        label = order[idx % len(order)]
        if buckets.get(label):
            picks.append(buckets[label].pop(0))
        idx += 1
        if all(len(buckets.get(l, [])) == 0 for l in order):
            break
    return picks

def extract_rubric_from_domain(domain: str) -> Dict[str, Any]:
    ds = load_domain_dataset(domain)
    return ds.get("rubric", {})
