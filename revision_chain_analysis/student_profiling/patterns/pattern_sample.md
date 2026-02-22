# Pattern samples

This folder contains small JSON examples used to test the
student AI use pattern classifier.

## Input format

Each JSON file has:

- `prompt_distribution`  dict with keys such as
  `generate_content`, `revise_content`, `understand_prompt`,
  `check_quality`
- `ps_indicators`  for example `self_authored_turns`
- `ct_indicators`  reserved for future features
- `expected_pattern`  the label we expect the classifier to return

Example:

```json
{
  "prompt_distribution": {
    "generate_content": 0.8,
    "revise_content": 0.1,
    "understand_prompt": 0.05,
    "check_quality": 0.05
  },
  "ps_indicators": { "self_authored_turns": 0 },
  "ct_indicators": {},
  "expected_pattern": "generator_only"
}
