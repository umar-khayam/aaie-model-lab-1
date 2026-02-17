"""
Validate prompt manifests against schema and uniqueness in the registry.
Refer to README.md and pipeline.md for usage details.
"""
import json
import os
import argparse
from typing import Dict, List

try:
    import jsonschema
except ImportError:
    jsonschema = None


def load_json(path: str) -> Dict:
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def normalize_key(s: str) -> str:
    return s.strip().lower()


def collect_manifests(candidates_dir: str, generated_dir: str) -> List[Dict]:
    manifests = []
    for root in [candidates_dir, generated_dir]:
        if not root or not os.path.isdir(root):
            continue
        for dirpath, _, filenames in os.walk(root):
            for fn in filenames:
                if fn.endswith('.json'):
                    path = os.path.join(dirpath, fn)
                    try:
                        manifests.append(load_json(path))
                    except Exception as e:
                        raise RuntimeError(f"Failed to load manifest {path}: {e}")
    return manifests


def validate_schema(items: List[Dict], schema_path: str):
    if not jsonschema:
        print("jsonschema not installed; skipping strict schema validation.")
        return
    schema = load_json(schema_path)
    for i, item in enumerate(items):
        try:
            jsonschema.validate(item, schema)
        except Exception as e:
            pid = item.get('id', f'item-{i}')
            msg = {
                "validated": False,
                "error": f"Schema validation failed for prompt {pid}",
                "details": [str(e)]
            }
            print(json.dumps(msg))
            raise SystemExit(4)


def ensure_unique(registry: Dict, new_items: List[Dict]):
    existing = registry.get('prompts', [])
    seen = {(normalize_key(p.get('id', '')), normalize_key(p.get('version', '')), normalize_key(p.get('status', '')))
            for p in existing}
    duplicates = []
    for item in new_items:
        key = (normalize_key(item.get('id', '')), normalize_key(item.get('version', '')), normalize_key(item.get('status', '')))
        if key in seen:
            duplicates.append({'id': item.get('id'), 'version': item.get('version'), 'status': item.get('status')})
    if duplicates:
        print(json.dumps({
            "validated": False,
            "error": "Duplicate entries found in registry",
            "details": duplicates
        }))
        raise SystemExit(5)


def verify_schema_refs(items: List[Dict], registry_file: str):
    # Resolve schema_ref against the absolute PromptWorkflow root
    # Given registry_file = PromptWorkflow/prompts/index.json
    # PromptWorkflow root = parent of the prompts directory
    from pathlib import Path
    prompts_dir = Path(registry_file).resolve().parent
    workflow_root = prompts_dir.parent  # PromptWorkflow
    for item in items:
        ref = item.get('schema_ref')
        if not ref:
            print(json.dumps({
                "validated": False,
                "error": f"Missing schema_ref in prompt {item.get('id')}",
                "details": []
            }))
            raise SystemExit(4)
        # Normalize ref to avoid double-prefix (e.g., PromptWorkflow/PromptWorkflow/...)
        ref_path = ref.replace('\\', '/').strip()
        if ref_path.startswith('PromptWorkflow/'):
            ref_path = ref_path[len('PromptWorkflow/'):]
        path = (workflow_root / ref_path).resolve()
        if not path.is_file():
            print(json.dumps({
                "validated": False,
                "error": f"schema_ref not found for prompt {item.get('id')}",
                "details": [str(path)]
            }))
            raise SystemExit(4)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--candidates-dir', required=False)
    parser.add_argument('--generated-dir', required=False)
    parser.add_argument('--registry-file', required=True)
    parser.add_argument('--schema', required=True)
    args = parser.parse_args()

    registry = load_json(args.registry_file)
    manifests = collect_manifests(args.candidates_dir, args.generated_dir)

    # Validate manifests and existing registry entries against schema
    validate_schema(manifests, args.schema)
    validate_schema(registry.get('prompts', []), args.schema)

    # Verify schema_ref paths for manifests
    verify_schema_refs(manifests, args.registry_file)

    # Ensure uniqueness versus registry
    ensure_unique(registry, manifests)

    print("Validation succeeded: schema + uniqueness + schema_ref")


if __name__ == '__main__':
    main()