# Prompt Workflow Pipeline

This pipeline validates, stages, smoke-tests, and promotes prompt manifests into the central registry (`prompts/index.json`). It is used in CI for PRs to `development**`.

## Key Folders for Pipeline
- `prompts/generated`: Auto-generated manifests from configs or tooling.
- `prompts/candidates`: Manifests awaiting promotion gates.
- `prompts/candidates/promoted`: Candidates that passed smoke tests.
- `prompts/candidates/failed`: Candidates that failed smoke tests.
- `prompts/index.json`: Central registry of prompts.
- `schemas/`: JSON Schemas for the prompt manifest and test outputs, e.g., `schemas/prompt_manifest.schema.json`, `schemas/evaluate.json`.

## Gates
- Schema validation: Ensures manifest conforms to `prompt_manifest.schema.json`.
- Render check: Validates `user_template` renders fully using each manifest’s `test_cases[0].inputs` (no placeholders).
- Smoke test: Calls FastAPI endpoint with `test_cases[0].inputs` and validates response against `schema_ref`.

## CI Flow (GitHub Actions)
1) Validate job
- Run folder-level schema validation and render check over `prompts/generated` and `prompts/candidates`.

2) Promote-to-staging job (on successful validate)
- Stage validated generated manifests into `prompts/candidates`.
- Cleanup `prompts/generated` (reflect deletions in Git).
- Smoke-test all candidates, update `prompts/index.json` atomically, and sort into `promoted`/`failed`.
- Cleanup root-level `prompts/candidates/*.json` (preserve `promoted`/`failed`).
- Commit registry updates and folder changes.
- Regenerate `docs/registry.md` and commit.

## Deduplication Method (Promotion of Multiple Prompt Files)
- Promotion avoids duplicates by replacing existing entries keyed by `(id, version, status, endpoint)`.
- `update_registry_md.py` deduplicates the summary using the same key.

## Conventions
- `status`: `dev | staging | production`.
- `schema_ref`: Path under `PromptWorkflow/`, e.g., `schemas/evaluate.json`.
- `test_cases`: Required; must include at least one case with `inputs`.
- Timestamps: `datetime.now(UTC).strftime('%Y-%m-%dT%H:%M:%SZ')`.
- Filenames: Windows-safe (no colons) `datetime.now(UTC).strftime('%Y-%m-%dT%H%M%SZ')`.

## Troubleshooting
- Smoke tests skipped locally: Ensure `prompts/candidates` has manifests; run staging step first.
- Promoted files missing after CI: Check commit step adds `prompts/index.json`, `promoted/*.json`, `failed/*.json` and that cleanup doesn’t remove subfolder files.
- Duplicate rows in registry: If a duplicate entry has already been committed to the registry, remove it manually, as CI may not necessarily see all prompt entries from the git commit.
- Duplicate rows in summary: Run `update_registry_md.py` after confirming registry deduplication during promotion.