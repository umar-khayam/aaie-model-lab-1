# Prompt Development Workflow - Version 1

This document contains instruction on how to use the PromptWorkflow version 1 (v1). 
Refer to the PromptWorkflow v1 handover documentation in the `aaie-documentation` repo for the design, roadmap, assumptions and constraints.

**<u>GenAI Usage Disclaimer</u>**

`GenAI` is used in the implementation of `PromptWorkflow v1`; however, all design, ideas, domain knowledge application, and code revision/testing are original.

## Versions

| Stages  | Version | Description                                                           | Compatible llm-pipeline API Version   | Comment   |
|---------|---------|-----------------------------------------------------------------------|----------|----------|
| Stage 1 | 1.0     | Local Dev Workflow + Automated Unit Test + Staging Promotion          | v1  | This version |

## Contents
- `prompts/index.json`: Registry of all prompt entries (authoritative validation target).
- `prompts/configs/`: Source configs (YAML/JSON) for generating prompt entries using `generate_prompt_entry.py`.
- `prompts/generated/`: Auto-generated prompt entry JSON files (pre-staging outputs).
- `prompts/candidates/`: Manifests staged for promotion gates.
	- `prompts/candidates/promoted/`: Candidates that passed smoke tests (v1) and any future unit tests.
	- `prompts/candidates/failed/`: Candidates that failed smoke tests (v1) and any future unit tests.
- `schemas/`: JSON Schemas used to validate the registry and test outputs.
- `scripts/`: CLI and helper scripts (e.g., `generate_prompt_entry.py`, `stage_candidates.py`, `promote_from_candidates.py`, `update_registry_md.py`).
- `.github/workflows/prompt-workflow.yml`: CI workflow v1 implementing validate → stage → promote → cleanup → summary.
- `app`: a lightweight FastAPI server for running smoked tests.
- `docs/pipeline.md`: End-to-end pipeline v1 overview and local commands.
- `docs/registry.md`: Auto-generated summary of current prompts.
- `README.md`: This guide.

## Usage

Fork the `aaie-model-lab` repo and create a local branch based on `development`.

### Push/PR Behaviours
- Developers can push freely to forked feature branches during development.
- The CI workflow is triggered on PR to `development**`:
	- Runs validation job and will fail the check if the registry is invalid, while surfacing `validated` and `warnings` outputs and printing error JSON to logs.
	- Runs promotion job if the validation job status is successful and will
		- Fail candidate prompts if any of the schema validation, API smoked test (this version) and future unit tests fail.
		- Promote candidate prompts if all tests pass.
		- Add the promoted prompts to index.json with status `staging`.
		- Perform post promotion cleanup (moving candidate prompts to `promoted` or `failed`) and refresh the prompt summary table in `docs/registry.md`.

For detailed description of the pipeline behaviours, refer to `docs/pipeline.md`

### Local Development Environment Setup (venv)
This is recommended for local development to keep dependencies isolated and make the PromptWorkflow portable.

PowerShell (Windows):

```
python -m venv .venv
./.venv/Scripts/Activate.ps1
python -m pip install -r PromptWorkflow/requirements.txt
```

Bash (macOS/Linux):

```
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r PromptWorkflow/requirements.txt
```

*Note:* CI in GitHub Actions installs dependencies per-job; it does not use the local venv.

### Running Scripts Locally
- `scripts/generate_prompt_entry.py`: Generate a prompt entry JSON from a YAML/JSON config.
	
	```
	python PromptWorkflow/scripts/generate_prompt_entry.py --config PromptWorkflow/prompts/configs/<config-file>.yaml
	```
	- Notes:
		- After generation, review the file in `prompts/generated/`
		- Refer to the guideline for detailed instructions on how to create config file: `\PromptWorkflow\docs\prompt_developer_guidelines.md`

- `scripts/validate_registry.py`: Validate the registry (single source of truth) against the schema and promotion gates.

	```
	python PromptWorkflow/scripts/validate_registry.py \
	  --registry-file PromptWorkflow/prompts/index.json \
	  --schema PromptWorkflow/schemas/prompt_manifest.schema.json \
	  --generated-dir PromptWorkflow/prompts/generated \
	  --candidates-dir PromptWorkflow/prompts/candidates
	```
-
- `scripts/render_check.py`: Ensure `user_template` renders without placeholders using manifest `test_cases`.

	```
	python PromptWorkflow/scripts/render_check.py --generated-dir PromptWorkflow/prompts/generated --candidates-dir PromptWorkflow/prompts/candidates
	```

- `scripts/stage_candidates.py`: Stage validated generated manifests into `prompts/candidates` (and clean `generated/`).

	```
	python PromptWorkflow/scripts/stage_candidates.py --generated-dir PromptWorkflow/prompts/generated --candidates-dir PromptWorkflow/prompts/candidates
	```

- `scripts/promote_from_candidates.py`: Smoke-test each candidate, update `prompts/index.json`, and move files to `promoted/` or `failed/`.

	```
	python PromptWorkflow/scripts/promote_from_candidates.py --candidates-dir PromptWorkflow/prompts/candidates --registry-file PromptWorkflow/prompts/index.json
	```

- `scripts/update_registry_md.py`: Regenerate `docs/registry.md` summary from `prompts/index.json`.

	```
	python PromptWorkflow/scripts/update_registry_md.py
	```
- `tests/test_smoke_mock.py` : Run smoke tests for all prompts in `candidates` folder.

	```
	pytest PromptWorkflow/tests/test_smoke_mock.py -q
	```

- Run all tests:

	```
	pytest PromptWorkflow/tests -q
	```


