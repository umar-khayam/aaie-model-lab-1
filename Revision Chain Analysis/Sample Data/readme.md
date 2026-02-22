## Schema Update and New Feature: Revision Chain Prompts

This data sample is based on the [aaie-Data-Hub/data/schema/schema.json](https://github.com/InnovAIte-Deakin/aaie-Data-Hub/blob/main/data/schema/schema.json), ensuring compatibility with existing evaluation and analysis pipelines. Building on the established structure, the sample now includes:

**Domain**: Defines the conversational area, e.g., "General Knowledge Chat".

**Prompt**: Describes the scenario or user request driving the chat session.

**Rubric**: Lists rigorous criteria such as Relevance & Engagement, Accuracy & Clarity, and Depth & Insight, with multiple performance descriptors under each for standardized assessment.

**Submissions**: Contains multiple submission instances, each with:

**final_submission**: The outcome after a full prompt revision cycle.

**label_type**: Now uniquely labeled as 'Human', 'AI', or 'Hybrid' to enable side-by-side analysis.

**prompt_chain**: Captures the detailed revision/dialogue process across multiple turns between user and AI, reflecting the evolving quality and focus of the feedback.

## Feature Addition: Revision Chain Prompting

This release introduces the Revision Chain feature:

- Each data entry includes three revision chains one purely human-driven, one AI-driven, and one hybrid demonstrating various interaction styles and feedback qualities.

- These chains make it easier to compare critical thinking, response depth, and adaptability between different feedback sources.

- The schema structure supports both qualitative rubric scoring and detailed prompt-by-prompt traceability.

This enhancement provides a richer foundation for analyzing feedback generation strategies, aligning closely with AAIE goals of supporting explainable, robust educational AI systems. Data sample and schema definitions remain compatible for reuse and further experimentation in upcoming streams.