# Engagement Depth Assessment

This module assesses how deeply students explored each rubric criterion
by analysing the language used in their questions and prompts.

It classifies engagement into three levels:

- **surface** – basic understanding  
  Examples: *what is, define, list, describe*

- **moderate** – reasoning or approach  
  Examples: *how, why, what approach, should I*

- **deep** – higher-order thinking  
  Examples: *compare, evaluate, synthesise, trade-offs, analyse*

The keyword rules used for this classification are defined in
`engagement_depth.yaml`.

## How it works

The Keyword Matching Engine groups student prompts by rubric criterion.
This module then:

1. Looks at the prompts for each criterion  
2. Searches for depth-related keywords  
3. Assigns the deepest matching level (surface, moderate, or deep)

## Depth scoring logic

For each rubric criterion, the module counts how many depth keywords appear
across the student prompts at each level (surface, moderate, deep).

- The level with the highest number of keyword matches is selected.
- If there is a tie, the deeper level wins (deep > moderate > surface).
- If no keywords match, the module returns **none**.

## Depth levels

- **none** – no depth indicators detected for that criterion
- **surface** – basic definition or recall questions (e.g. what is, define, list)
- **moderate** – explanatory or process questions (e.g. how, why, what steps)
- **deep** – higher-order thinking (e.g. compare, evaluate, analyse, trade-offs)

## Main functions

- **`assess_engagement_depth`**  
  Analyses the prompts for a single rubric criterion and returns one depth label.

- **`assess_all_criteria`**  
  Applies the depth assessment across all criteria and returns a dictionary
  mapping each `criteria_id` to its engagement depth.
