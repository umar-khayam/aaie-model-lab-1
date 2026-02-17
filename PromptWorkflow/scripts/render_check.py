"""
Render-check prompt manifests to ensure templates fully render with test case inputs.
Refer to README.md for usage details.
"""
import json
import os
import argparse
from typing import Dict, List


def load_json(path: str) -> Dict:
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def collect_manifests(paths: List[str]) -> List[Dict]:
    items = []
    for root in paths:
        if not root or not os.path.isdir(root):
            continue
        for dirpath, _, filenames in os.walk(root):
            for fn in filenames:
                if fn.endswith('.json'):
                    with open(os.path.join(dirpath, fn), 'r', encoding='utf-8') as f:
                        items.append(json.load(f))
    return items


def has_placeholders(render: str) -> bool:
    return ('{{' in render) or ('}}' in render) or ('${' in render) or ('}' in render and '${' in render)


def render_user_template(tpl: str, vars_obj: Dict) -> str:
    # Support ${var} style; simple replace for sanity check only
    out = tpl
    for k, v in vars_obj.items():
        out = out.replace('${' + k + '}', str(v))
        out = out.replace('{{' + k + '}}', str(v))
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--candidates-dir', required=False)
    parser.add_argument('--generated-dir', required=False)
    args = parser.parse_args()

    manifests = collect_manifests([args.candidates_dir, args.generated_dir])
    if not manifests:
        print("No manifests to render-check; skipping.")
        return

    for m in manifests:
        tpl = m.get('user_template', '')
        if not tpl:
            raise AssertionError(f"Manifest id={m.get('id')} missing user_template")

        test_cases = m.get('test_cases', [])
        if not test_cases:
            raise AssertionError(f"Manifest id={m.get('id')} missing required test_cases")
        inputs = test_cases[0].get('inputs')
        if not isinstance(inputs, dict) or not inputs:
            raise AssertionError(f"Manifest id={m.get('id')} has invalid test_cases[0].inputs")

        rendered = render_user_template(tpl, inputs)
        if has_placeholders(rendered):
            raise AssertionError(f"Placeholders remain after render for id={m.get('id')}")

    print("Render check succeeded: templates fully render with manifest test_cases")


if __name__ == '__main__':
    main()
