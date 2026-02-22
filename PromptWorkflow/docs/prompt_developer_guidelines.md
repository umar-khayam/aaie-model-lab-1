# Prompt Developer Guidelines (PromptWorkflow)

Guidelines for prompt engineers to work with the PromptWorkflow pipeline for validating, staging, smoke-testing, and promoting prompt manifests into the central registry.

## Process Overview
- Author prompts in your experimental script or notebook.
- Capture required fields in a YAML/JSON config.
- Generate a timestamped prompt entry JSON to `prompts/generated`.
- Open a PR to a `development**` branch; CI validates and stages candidates.
- CI runs smoke tests on `prompts/candidates` and promotes passing entries to the registry.
- Current gate: `dev` → `staging`. (`staging` → `production` is not yet implemented.)

## What to Include in Your Manifest
- `system_message`: LLM role text.
- `user_template`: message template with variables like `{{text}}`, `{{domain}}`.
- `variables`: list of `{name, type, required}`.
- `task` (optional): logical use-case label if needed.
- `endpoint` and `api_version`: REST path (prefix must match `/api/v1/` vs `/api/v2/`).
- `schema_ref`: path under `PromptWorkflow/` to the expected response schema (e.g., `schemas/evaluate.json`).
- `test_cases`: required; at least one case with `inputs`. Assertions optional.
- Optional: `fewshot_refs`, `rollout`, `reviewed_by`, `approvals` (for future gates).

## Config-Driven Generation (YAML)
Config files can be stored in `PromptWorkflow/prompts/configs/`.
Example simple YAML config file:
```
# analyze_rc_profile_v1.yaml
# task is optional in v1 or v2; include for future usage
task: rc_profile
endpoint: /api/v1/rc_profile
api_version: v1
schema_ref: schemas/rc_profile.json
created_by: dev@example.com
variables:
  - name: text
    type: string
    required: true
system_message: "You are a helpful assistant."
user_template: "text: {{ text }}"
test_cases:
  - name: smoke
    inputs: { text: "sample" }
    assertions: []
```

Generate the prompt entry JSON:
```
python PromptWorkflow/scripts/generate_prompt_entry.py \
  --config PromptWorkflow/prompts/configs/analyze_rc_profile_v1.yaml \
  --output-dir PromptWorkflow/prompts/generated
```
Outputs: `PromptWorkflow/prompts/generated/<id>.<YYYY-MM-DDTHHMMSSZ>.json`
- `id` format: `<task>.<slug>.<api_version>` (e.g., `rc_profile.default.v1`).
- `version`: semantic version with a `changelog` entry dated in UTC.
- `test_cases` must be present; include at least one case with `inputs`.

*Notes:* 
-`<slug>` is a short friendly prompt identifier and used in building the prompt `id`; if not provided in config, `default` is used.
- Timestamps in manifests use UTC: `YYYY-MM-DDTHH:MM:SSZ`

## Registry Flow (CI-managed)
- Do not manually paste entries into `prompts/index.json`.
- CI stages validated generated manifests into `prompts/candidates/`.
- CI smoke-tests candidates against the local FastAPI app and promotes passing entries by updating `prompts/index.json` atomically, then moves files into `prompts/candidates/promoted/` or `prompts/candidates/failed/`.
- Promotion avoids duplicates by replacing entries keyed by `(id, version, status, endpoint)`.
- The `docs/registry.md` summary is regenerated in CI and deduplicated using the same key.

## Local Validation (venv recommended)
```
python -m pip install -r PromptWorkflow/requirements.txt
# Validate schemas and render checks on generated and candidates
python PromptWorkflow/scripts/validate_registry.py --paths PromptWorkflow/prompts/generated PromptWorkflow/prompts/candidates --schema PromptWorkflow/schemas/prompt_manifest.schema.json
python PromptWorkflow/scripts/render_check.py --paths PromptWorkflow/prompts/generated PromptWorkflow/prompts/candidates
# Stage and smoke-test locally (optional before PR)
python PromptWorkflow/scripts/stage_candidates.py --source PromptWorkflow/prompts/generated --dest PromptWorkflow/prompts/candidates
python PromptWorkflow/scripts/promote_from_candidates.py --candidates PromptWorkflow/prompts/candidates --registry PromptWorkflow/prompts/index.json --app PromptWorkflow/app/main.py
python PromptWorkflow/scripts/update_registry_md.py --registry PromptWorkflow/prompts/index.json --out PromptWorkflow/docs/registry.md
```
Common fixes for validation errors:
- `api_version` must match `endpoint` prefix (`/api/v1/` or `/api/v2/`).
- `test_cases` must include at least one case with `inputs`.
- `changelog` must be an array of `{version, date, changes}` objects.

## Promotion Gates
- `dev` → `staging`: requires `test_cases` present and smoke tests passing.
- `staging` → `production`: planned; will require system integration tests passing and manual `approvals` in addition to staging requirements.

## CI (Pull Request)
- Commit changes under `PromptWorkflow/**` and open a PR to a `development**` branch.
- Validate job: folder-level schema validation and render check over `prompts/generated` and `prompts/candidates`.
- Promote-to-staging job: stage generated to candidates, smoke-test all candidates using in-process FastAPI TestClient (no external server needed), update `prompts/index.json` atomically with dedup, sort candidate files into `promoted`/`failed`, clean up root-level `prompts/candidates/*.json`, regenerate `docs/registry.md`, and commit changes.

## ID and Versioning Guidance
- ID generation: `id = <task>.<slug>.<api_version>`.
- Keep semantic `version` separate from `id`; update `changelog` with each change.
- Suggested bump approach:
  - Patch: template wording/metadata.
  - Minor: new variables or expanded assertions.
  - Major: task/endpoint changes or breaking variable/response expectations.

## Good Practices
- Keep prompts self-contained and portable within `PromptWorkflow`.
- Use `fewshot_refs` and sample data to strengthen `test_cases`.
- Prefer small, focused single-prompt PRs; include a descriptive `changelog` entry. Though multiple files promotion is supported, running CI on large number of prompt files will affect performance as tests are iterated over each file and deduplication is required.
- Ensure `user_template` renders fully with `test_cases[0].inputs` (no unresolved placeholders).