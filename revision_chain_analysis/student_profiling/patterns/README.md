# Student AI Use Pattern Classifier

This module assigns a simple label that describes how a student uses the AI
assistant during a revision chain.

## Patterns

- `generator_only`  mostly asks the AI to write content.
- `reviser`  writes their own text and uses the AI to revise it.
- `planner_checker`  focuses on planning, understanding the prompt, and checking quality.
- `mixed`  no strong pattern, or a blend of the others.

## Rules (MVP)

Given `prompt_distribution` with keys:

- `generate_content`
- `revise_content`
- `understand_prompt`
- `check_quality`

and `ps_indicators["self_authored_turns"]`:

1. If `generate_content >= 0.60` -> `generator_only`  
2. Else if `revise_content >= 0.40` and `self_authored_turns ≥ 2` -> `reviser`  
3. Else if `understand_prompt + check_quality >= 0.50` -> `planner_checker`  
4. Else -> `mixed`  

Rule order also works as the tie break.

## Files in this folder

- `pattern_classifier.py`  
  Main rule based classifier and pattern constants.

- `pattern_samples/generator_only_sample.json`  
- `pattern_samples/reviser_sample.json`  
- `pattern_samples/planner_checker_sample.json`  
- `pattern_samples/boundary_generator_vs_reviser_sample.json`  
  Curated examples with `prompt_distribution`, `ps_indicators`,
  `ct_indicators`, and `expected_pattern`.

- `pattern_samples/test_pattern_classifier.py`  
  Pytest tests that load the samples and check the classifier.

- `pattern_sample.md`  
  Extra notes about the sample JSON format and how to run the tool on them.

## Running on sample JSONs

To run the classifier on all pattern samples and save outputs, use:

```bash
python revision_chain_analysis/student_profiling/tools/run_pattern_samples.py
