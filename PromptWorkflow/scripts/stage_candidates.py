"""
Stage validated generated prompt manifests into candidates folder.
Refer to README.md and pipeline.md for usage details.
"""
import argparse
import json
import os
import shutil
from pathlib import Path


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def list_manifests(root: Path):
    items = []
    if root.is_dir():
        for p in sorted(root.glob("*.json")):
            items.append(p)
    return items


def main():
    parser = argparse.ArgumentParser(description="Stage validated generated manifests into candidates folder")
    parser.add_argument("--generated-dir", required=True)
    parser.add_argument("--candidates-dir", required=True)
    parser.add_argument("--registry-file", required=False)
    args = parser.parse_args()

    gen_root = Path(args.generated_dir).resolve()
    cand_root = Path(args.candidates_dir).resolve()
    cand_root.mkdir(parents=True, exist_ok=True)

    copied = 0
    for src in list_manifests(gen_root):
        # Load to ensure it's valid JSON and has required minimal fields
        try:
            data = load_json(src)
        except Exception as e:
            print(f"Skip invalid JSON: {src} ({e})")
            continue
        required_keys = ["id", "version", "status", "endpoint", "api_version", "user_template", "variables", "test_cases"]
        if not all(k in data for k in required_keys):
            print(f"Skip incomplete manifest (missing required keys): {src}")
            continue
        # Copy preserving filename; overwrite if exists to reflect latest validated output
        dst = cand_root / src.name
        shutil.copy2(src, dst)
        copied += 1
        try:
            src.unlink()
        except Exception as e:
            print(f"Warning: failed to delete staged file {src}: {e}")

    print(f"Staged {copied} generated manifest(s) to candidates and cleaned generated folder: {cand_root}")


if __name__ == "__main__":
    main()
