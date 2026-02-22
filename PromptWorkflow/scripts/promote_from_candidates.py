"""
Promote candidate prompt manifests to registry after smoke tests.
Refer to README.md for usage details.
"""
import argparse
import json
import os
from pathlib import Path

from fastapi.testclient import TestClient
from jsonschema import validate as json_validate


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def app_instance(repo_root: Path):
    # Prefer local PromptWorkflow app
    local_app_path = repo_root / "PromptWorkflow" / "app"
    if local_app_path.is_dir():
        import sys
        sys.path.insert(0, str(local_app_path))
        try:
            from main import app  # type: ignore
            return app
        except Exception:
            pass
    # Fallbacks (optional): API Integration or Deployment
    api_int_path = repo_root / "API Integration" / "llm-api-pipeline" / "app"
    if api_int_path.is_dir():
        import sys
        sys.path.insert(0, str(api_int_path))
        try:
            from main import app  # type: ignore
            return app
        except Exception:
            pass
    deploy_path = repo_root / "Deployment" / "src"
    if deploy_path.is_dir():
        import sys
        sys.path.insert(0, str(deploy_path))
        try:
            from main import app  # type: ignore
            return app
        except Exception:
            pass
    raise RuntimeError("FastAPI app not found for promotion smoke tests")


def write_atomic(path: Path, data: dict):
    tmp = Path(str(path) + ".tmp")
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    os.replace(tmp, path)


def main():
    parser = argparse.ArgumentParser(description="Promote candidates to registry after smoke tests; move results to promoted/failed")
    parser.add_argument("--candidates-dir", required=True)
    parser.add_argument("--registry-file", required=True)
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    workflow_root = repo_root / "PromptWorkflow"
    cand_root = (workflow_root / args.candidates_dir).resolve() if not args.candidates_dir.startswith(str(workflow_root)) else Path(args.candidates_dir)
    if not cand_root.is_dir():
        cand_root = Path(args.candidates_dir).resolve()
    promoted_dir = cand_root / "promoted"
    failed_dir = cand_root / "failed"
    promoted_dir.mkdir(parents=True, exist_ok=True)
    failed_dir.mkdir(parents=True, exist_ok=True)

    registry_path = (workflow_root / args.registry_file).resolve() if not args.registry_file.startswith(str(workflow_root)) else Path(args.registry_file)
    if not registry_path.is_file():
        registry_path = Path(args.registry_file).resolve()
    registry = load_json(registry_path)
    prompts = registry.get("prompts", [])

    app = app_instance(repo_root)
    client = TestClient(app)

    total = 0
    passed = 0
    failed = 0
    for manifest_path in sorted(cand_root.glob("*.json")):
        total += 1
        manifest = load_json(manifest_path)

        endpoint = manifest.get("endpoint")
        test_cases = manifest.get("test_cases", [])
        schema_ref = manifest.get("schema_ref")
        if not (endpoint and test_cases and schema_ref):
            manifest_path.replace(failed_dir / manifest_path.name)
            failed += 1
            continue
        inputs = test_cases[0].get("inputs", {})
        schema_path = (workflow_root / schema_ref).resolve()
        schema = load_json(schema_path)

        try:
            resp = client.post(endpoint, json=inputs)
            if resp.status_code != 200:
                raise AssertionError(f"HTTP {resp.status_code}: {resp.text}")
            payload = resp.json()
            json_validate(instance=payload, schema=schema)
        except Exception:
            manifest_path.replace(failed_dir / manifest_path.name)
            failed += 1
            continue

        # Passed: set status to staging and append to registry avoiding duplicates
        manifest["status"] = "staging"
        key = (manifest.get("id", ""), manifest.get("version", ""), manifest.get("status", ""), manifest.get("endpoint", ""))
        existing_idx = None
        for i, p in enumerate(prompts):
            if (p.get("id", ""), p.get("version", ""), p.get("status", ""), p.get("endpoint", "")) == key:
                existing_idx = i
                break
        if existing_idx is not None:
            # Replace existing entry with latest details
            prompts[existing_idx] = manifest
        else:
            prompts.append(manifest)
        write_atomic(registry_path, {"registry_version": registry.get("registry_version", "1.0.0"), "prompts": prompts})
        manifest_path.replace(promoted_dir / manifest_path.name)
        passed += 1

    print(json.dumps({"total": total, "passed": passed, "failed": failed, "promoted_dir": str(promoted_dir), "failed_dir": str(failed_dir)}, indent=2))


if __name__ == "__main__":
    main()
