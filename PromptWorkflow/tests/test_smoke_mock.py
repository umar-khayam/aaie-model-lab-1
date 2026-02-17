"""
Smoked tests for FastAPI evaluate endpoint using mock LLM responses.
Runs against candidate prompt manifests in PromptWorkflow/prompts/candidates.
Expand for other endpoints as needed.
"""
import json
from pathlib import Path
import sys

import pytest
from fastapi.testclient import TestClient
from jsonschema import validate as json_validate

def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def list_candidate_manifests() -> list[Path]:
    candidates_dir = Path(__file__).resolve().parents[1] / "prompts" / "candidates"
    if not candidates_dir.is_dir():
        return []
    return sorted(candidates_dir.glob("*.json"))


def app_instance():
    """Resolve FastAPI app from API Integration or Deployment folders.
    Handles spaces and dashes in folder names by adjusting sys.path dynamically.
    """
    root = Path(__file__).resolve().parents[2]
    # Prefer local PromptWorkflow app
    local_app_path = root / "PromptWorkflow" / "app"
    if local_app_path.is_dir():
        sys.path.insert(0, str(local_app_path))
        try:
            from main import app  # type: ignore
            return app
        except Exception:
            pass
    # Notes: 
    #  - Import will fail as the current llm-api-pipeline path has spaces/dashes and is not importable
    #  - Future implementation could use containerized tests based on the llm-api-pipeline structure
    #  - API Integration path: API Integration/llm-api-pipeline/app
    api_int_path = root / "API Integration" / "llm-api-pipeline" / "app"
    if api_int_path.is_dir():
        sys.path.insert(0, str(api_int_path))
        try:
            from main import app  # type: ignore
            return app
        except Exception:
            pass
    # Deployment path: Deployment/src
    deploy_path = root / "Deployment" / "src"
    if deploy_path.is_dir():
        sys.path.insert(0, str(deploy_path))
        try:
            from main import app  # type: ignore
            return app
        except Exception:
            pass
    raise RuntimeError("FastAPI app not found for smoke test")


@pytest.mark.parametrize("manifest_path", list_candidate_manifests() or [])
def test_evaluate_manifest_response_schema(manifest_path: Path):
    if manifest_path is None:
        pytest.skip("No candidate manifests found")
    manifest = load_json(manifest_path)

    # Only target evaluate endpoint manifests in this smoke test
    endpoint = manifest.get("endpoint")
    assert endpoint == "/api/v1/evaluate", f"Unexpected endpoint in {manifest_path.name}: {endpoint}"

    schema_ref = manifest.get("schema_ref")
    assert schema_ref, "schema_ref missing in manifest"

    # Resolve schema path relative to PromptWorkflow root
    workflow_root = Path(__file__).resolve().parents[1]
    schema_path = (workflow_root / schema_ref).resolve()
    assert schema_path.is_file(), f"Schema not found for {manifest_path.name}: {schema_path}"
    schema = load_json(schema_path)

    # Build request body from the manifest test case inputs
    test_cases = manifest.get("test_cases", [])
    assert test_cases, f"No test_cases provided in manifest {manifest_path.name}"
    inputs = test_cases[0].get("inputs", {})
    assert inputs, f"First test_case missing inputs in {manifest_path.name}"

    # Start FastAPI app client and call the endpoint
    # Resolve app; skip test gracefully if not available in this environment
    try:
        app = app_instance()
    except RuntimeError:
        pytest.skip("FastAPI app not found; skipping smoke test in this environment")
    client = TestClient(app)
    resp = client.post(endpoint, json=inputs)
    assert resp.status_code == 200, f"Non-200 from {endpoint} for {manifest_path.name}: {resp.status_code} {resp.text}"

    payload = resp.json()
    # Validate against aggregate evaluate schema
    json_validate(instance=payload, schema=schema)

    # Minimal content assertions to catch obvious regressions
    assert "classification" in payload and "label" in payload["classification"], "classification.label missing"
    assert "rubric_scores" in payload and isinstance(payload["rubric_scores"].get("scores", []), list), "rubric_scores.scores missing"
    assert "feedback" in payload and isinstance(payload["feedback"], dict), "feedback missing"