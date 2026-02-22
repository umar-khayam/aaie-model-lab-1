"""Tests for prompt registry cases to ensure test cases cover required variables,
user template renders, and assertions have expected shape.
To be replaced with proper Unit tests in the future."""

import json
import re
from pathlib import Path

INDEX = Path("PromptWorkflow/prompts/index.json")


def load_prompts():
    data = json.loads(INDEX.read_text(encoding="utf-8"))
    assert "prompts" in data and isinstance(data["prompts"], list)
    return data["prompts"]


def _required_var_names(prompt):
    return [v["name"] for v in (prompt.get("variables") or []) if v.get("required")]


def _render_user_template(template: str, inputs: dict) -> str:
    def repl(m):
        key = m.group(1)
        return str(inputs.get(key, f"{ { 'MISSING:' + key } }"))
    return re.sub(r"\$\{([^}]+)\}", repl, template)


def test_cases_inputs_cover_required_variables():
    for p in load_prompts():
        required = set(_required_var_names(p))
        for case in (p.get("test_cases") or []):
            inputs = case.get("inputs") or {}
            missing = [n for n in required if n not in inputs]
            assert not missing, f"{p.get('id')}:{case.get('name')} missing required vars: {missing}"


def test_user_template_renders_without_placeholders():
    for p in load_prompts():
        template = p.get("user_template") or ""
        for case in (p.get("test_cases") or []):
            rendered = _render_user_template(template, case.get("inputs") or {})
            assert "${" not in rendered, f"{p.get('id')}:{case.get('name')} template left placeholders"


def test_assertions_have_expected_shape():
    for p in load_prompts():
        for case in (p.get("test_cases") or []):
            assertions = case.get("assertions") or []
            for a in assertions:
                if isinstance(a, dict) and "type" in a and "target" in a and "value" in a:
                    assert isinstance(a["type"], str) and a["type"], "assertion.type must be non-empty string"
                    assert isinstance(a["target"], str) and a["target"], "assertion.target must be non-empty string"
                    assert isinstance(a["value"], (list, str, int, float, dict)), "assertion.value unexpected type"
                    if a["type"] == "contains":
                        assert isinstance(a["value"], list) and all(isinstance(x, str) for x in a["value"]), "contains.value must be list[str]"
                else:
                    # Compact map style: { "path": [ ... ] }
                    for k, v in a.items():
                        assert isinstance(k, str) and k, "assertion key must be non-empty string path"
                        assert isinstance(v, list), "compact assertion value must be a list"
                        assert all(isinstance(x, str) for x in v), "compact assertion list must contain strings"


def test_endpoint_aligns_with_api_version():
    for p in load_prompts():
        api = p.get("api_version")
        ep = p.get("endpoint", "")
        if api == "v1":
            assert ep.startswith("/api/v1/"), f"{p.get('id')}: endpoint must start with /api/v1/"
        elif api == "v2":
            assert ep.startswith("/api/v2/"), f"{p.get('id')}: endpoint must start with /api/v2/"
