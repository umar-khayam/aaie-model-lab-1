"""
Promote candidate and generated prompt manifests to staging in the registry.
Refer to README.md for usage details.
"""
import json
import os
import argparse
from datetime import datetime, UTC


def load_json(path: str):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def write_atomic(path: str, data: dict):
    tmp = path + ".tmp"
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2, sort_keys=True)
    os.replace(tmp, path)


def collect_manifests(root: str):
    items = []
    if root and os.path.isdir(root):
        for dirpath, _, filenames in os.walk(root):
            for fn in filenames:
                if fn.endswith('.json'):
                    with open(os.path.join(dirpath, fn), 'r', encoding='utf-8') as f:
                        items.append(json.load(f))
    return items


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--candidates-dir', required=False)
    parser.add_argument('--generated-dir', required=False)
    parser.add_argument('--registry-file', required=True)
    parser.add_argument('--provenance', required=False, help='commit_sha,run_id')
    args = parser.parse_args()

    registry = load_json(args.registry_file)
    prompts = registry.get('prompts', [])

    to_promote = collect_manifests(args.candidates_dir) + collect_manifests(args.generated_dir)
    now = datetime.now(UTC).strftime('%Y-%m-%dT%H:%M:%SZ')
    prov_parts = (args.provenance or ',').split(',')
    commit_sha = prov_parts[0] if len(prov_parts) > 0 else ''
    run_id = prov_parts[1] if len(prov_parts) > 1 else ''

    for m in to_promote:
        m['status'] = 'staging'
        changelog = m.get('changelog', [])
        changelog.append({
            'date': now,
            'description': 'Promoted to staging via CI',
            'commit_sha': commit_sha,
            'run_id': run_id
        })
        m['changelog'] = changelog
        prompts.append(m)

    registry['prompts'] = prompts
    write_atomic(args.registry_file, registry)
    print(f"Promoted {len(to_promote)} prompts to staging and updated registry")


if __name__ == '__main__':
    main()
