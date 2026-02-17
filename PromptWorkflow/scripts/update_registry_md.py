"""
Update the registry markdown summary from the prompt registry JSON.
Refer to README.md and pipeline.md for usage details.
"""
import json
from pathlib import Path


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def to_list(val):
    if val is None:
        return []
    if isinstance(val, list):
        return val
    return [str(val)]


def generate_markdown(registry: dict) -> str:
    prompts = registry.get("prompts", [])
    # Deduplicate by (id, version, status, endpoint)
    seen = {}
    for p in prompts:
        key = (p.get("id", ""), p.get("version", ""), p.get("status", ""), p.get("endpoint", ""))
        # Prefer the latest author/review fields if duplicates occur
        seen[key] = p

    # Sort by id then version (semver-ish as string) then status
    sorted_items = sorted(
        seen.values(),
        key=lambda x: (x.get("id", ""), x.get("version", ""), x.get("status", ""))
    )

    lines = []
    lines.append("# Prompt Registry Summary\n")
    lines.append("")
    lines.append("| Prompt ID | Version | API Endpoint | Status | Author | Reviewers | Approvers |")
    lines.append("|-----------|---------|--------------|--------|--------|-----------|----------|")
    for p in sorted_items:
        pid = p.get("id", "")
        ver = p.get("version", "")
        ep = p.get("endpoint", "")
        status = p.get("status", "")
        author = p.get("created_by", p.get("author", ""))
        reviewers = to_list(p.get("reviewed_by"))
        approvers = to_list(p.get("approvals"))
        lines.append(f"| {pid} | {ver} | {ep} | {status} | {author} | {', '.join(reviewers)} | {', '.join(approvers)} |")
    lines.append("")
    return "\n".join(lines)


def main():
    workflow_root = Path(__file__).resolve().parents[1]
    registry_path = workflow_root / "prompts" / "index.json"
    out_path = workflow_root / "docs" / "registry.md"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    registry = load_json(registry_path)
    md = generate_markdown(registry)
    out_path.write_text(md, encoding="utf-8")
    print(f"Wrote summary to {out_path}")


if __name__ == "__main__":
    main()
