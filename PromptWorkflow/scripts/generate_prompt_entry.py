"""
Generate a prompt entry JSON file from a config file.
Refer to README.md and prompt_developer_guidliens.md for usage details.
"""
import argparse
import json
from datetime import datetime, UTC
from pathlib import Path
from typing import Any, Dict
import yaml


def sanitize_filename(s: str) -> str:
    return s.replace("/", "_").replace("\\", "_")


def make_id(task: str | None, slug: str, api_version: str) -> str:
    safe_slug = (slug or "default").strip().lower().replace(" ", "-")
    if task:
        return f"{task}.{safe_slug}.{api_version}"
    # If task is not provided, build id without task segment
    return f"{safe_slug}.{api_version}"


def load_config_any(path: Path) -> Dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() in {".yml", ".yaml"}:
        data = yaml.safe_load(text)
        if data is None:
            raise ValueError(f"Empty or invalid YAML config: {path}")
        if not isinstance(data, dict):
            raise ValueError(f"YAML config must be a mapping/object: {path}")
        return data
    data = json.loads(text)
    if not isinstance(data, dict):
        raise ValueError(f"JSON config must be an object: {path}")
    return data


def build_entry_from_config(cfg: Dict[str, Any]) -> Dict[str, Any]:
    pid = cfg.get("id") or make_id(cfg.get("task"), cfg.get("slug", "default"), cfg["api_version"])
    variables = cfg.get("variables") or [{"name": "text", "type": "string", "required": True}]
    user_template = cfg.get("user_template") or " ".join([f"{v['name']}: {{{{ {v['name']} }}}}" for v in variables])

    entry: Dict[str, Any] = {
        "id": pid,
        "version": cfg.get("version", "1.0.0"),
        "status": cfg.get("status", "dev"),
        "task": cfg.get("task"),
        "endpoint": cfg["endpoint"],
        "api_version": cfg["api_version"],
        "schema_ref": cfg["schema_ref"],
        "system_message": cfg.get("system_message", "You are a helpful assistant."),
        "user_template": user_template,
        "variables": variables,
        "fewshot_refs": cfg.get("fewshot_refs", []),
        "test_cases": cfg.get("test_cases")
        or [
            {
                "name": "smoke",
                "inputs": {v["name"]: f"sample_{v['name']}" for v in variables},
                "assertions": [],
            }
        ],
        "rollout": cfg.get("rollout", {}),
        "created_by": cfg.get("created_by", "unknown"),
        "reviewed_by": cfg.get("reviewed_by"),
        "approvals": cfg.get("approvals"),
        "changelog": cfg.get("changelog")
        or [
            {
                "version": cfg.get("version", "1.0.0"),
                "date": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "changes": "Initial version",
            }
        ],
    }

    # Remove keys with None to keep output tidy
    return {k: v for k, v in entry.items() if v is not None}


def main():
    parser = argparse.ArgumentParser(description="Generate a prompt entry JSON file from a config")
    parser.add_argument("--config", required=True, help="Path to JSON config with prompt fields")
    parser.add_argument(
        "--output-dir",
        default=str(Path(__file__).resolve().parents[1] / "prompts" / "generated"),
        help="Directory to write the generated prompt JSON",
    )

    args = parser.parse_args()
    cfg_path = Path(args.config)
    out_dir = Path(args.output_dir)

    if not cfg_path.exists():
        print(json.dumps({"error": f"Config not found: {cfg_path}"}))
        raise SystemExit(2)

    cfg = load_config_any(cfg_path)

    # Validate required keys (task is optional per v2 API design)
    required = ["endpoint", "api_version", "schema_ref"]
    missing = [k for k in required if k not in cfg]
    if missing:
        print(json.dumps({"error": f"Missing required config keys: {', '.join(missing)}"}))
        raise SystemExit(3)

    # Normalize test_cases: allow 'input' key as alias for 'inputs'
    if isinstance(cfg.get("test_cases"), list):
        normalized = []
        for tc in cfg["test_cases"]:
            if isinstance(tc, dict) and "input" in tc and "inputs" not in tc:
                tc = {**tc}
                tc["inputs"] = tc.pop("input")
            normalized.append(tc)
        cfg["test_cases"] = normalized

    entry = build_entry_from_config(cfg)
    pid = entry["id"]
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(UTC).strftime("%Y-%m-%dT%H%M%SZ")
    out_file = out_dir / f"{sanitize_filename(pid)}.{ts}.json"
    out_file.write_text(json.dumps(entry, indent=2), encoding="utf-8")
    print(json.dumps({"written": str(out_file), "id": pid}))


if __name__ == "__main__":
    main()
