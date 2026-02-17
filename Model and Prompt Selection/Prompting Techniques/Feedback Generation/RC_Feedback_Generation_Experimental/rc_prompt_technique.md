# Prompting Technique for Revision Chains  
**Artificial Assessment Intelligence for Educators (AAIE)**  
**Module:** Feedhack Generation for RCA  
**Author:** Steven Christolis
**Date:** November 26, 2025
**Version:** 0.2  

---

## 1. Background

In T2 2025 to prompts were developed to provide AI detection and Feedback Generation.

As part of T3 2025, additional work is being done to analyse a students LLM chat history to determine if the student is using the LLM as tool for learning, critical thinking and problem-solving. 

The work covered in this document sits within the Feedback Generation (FG) scope. While the file primarily focuses on Revision Chain Analysis (RCA), the outcomes and documentation ultimately support FG.

The purpose of this document is to define an initial prompt to be used as part of Feedack Generation.

## 2. Design overview

The new prompt is based on the T2 2025 Feedback Generation prompt so that it can easily fit withing the existing pipelines developed.

The following techniques were used to develop the prompt

| **Prompt Technique** | **Implementation** |
|---------------------|---------------------|
| Role Based | "You are an expert educational feedback generator" |
| Structured Output | Explicit format template with separators |
| Instruction-Based | Numbered evaluation instructions |
| Constraint-Based | "Do NOT" lists, common mistakes |

The prompt uses a hybrid approach that combines multiple techniques, which is best for complex evaluation tasks like this. The heavy constraints and explicit formatting are necessary to provide reliable, consistent, structured output for educational assessment.

In addition to the updating of the prompt, a custom revision chain rubric was also defined to improve the output of the prompt.

A decision was made not to use few-shot prompting technique or chain of thought prompting.

Few shot prompting is useful when there are specific examples but is not as useful where every submission is unique as is the case in this instance.

Chain of thought prompting may provide some additional improvement but the initial output produced was reasonable and this additional prompting complexity is not required at this stage.

The prompt has been saved in a Jupyter notebook so that the relevant code can be easily run and improved upon.

## 3. Detailed Design

### 3.1 Prompt Purpose
This prompt system evaluates **student learning behaviours** during interactions with Large Language Models (LLMs), specifically analysing whether students demonstrate active learning strategies versus passive answer extraction.

### 3.2 Prompt Structure
```
┌─────────────────────────────────────────┐
│     SYSTEM_PROMPT (Role & Rules)        │
│  - Role assignment                      │
│  - Critical constraints                 │
│  - Evaluation focus                     │
└─────────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────┐
│   STRUCTURED_OUTPUT_PROMPT (Format)     │
│  - Output template                      │
│  - Section structure                    │
│  - Length constraints                   │
└─────────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────┐
│   Runtime Context (Fed at Execution)    │
│  - Rubric criteria                      │
│  - Student prompts                      │
│  - Full conversation                    │
│  - Evaluation instructions              │
└─────────────────────────────────────────┘
```

### 3.3 Prompting Techniques Used

| Technique | Implementation | Purpose |
|-----------|----------------|---------|
| **Role-Based** | "You are an expert educational feedback generator" | Establishes expertise and tone |
| **Constraint-Based** | "⚠️ CRITICAL INSTRUCTION" with DO NOT lists | Prevents common evaluation errors |
| **Structured Output** | Template with separators and placeholders | Ensures consistent, parseable output |
| **Example-Based** | Micro-examples (✓/✗) embedded in instructions | Clarifies correct vs incorrect analysis |
| **Template-Driven** | Fixed format with defined sections | Facilitates automated processing |

### 3.4 Prompt Assembly
```python
final_prompt = f"""
{SYSTEM_PROMPT}

TASK CONTEXT:
You are assessing a STUDENT's inquiry and learning process from the domain: **{domain}**.
The assignment prompt is:
\"\"\"{assignment_prompt}\"\"\"

ASSESSMENT RUBRIC:
{rubric_text}

═══════════════════════════════════════════════════════════
STUDENT'S PROMPTS (What the student actually typed):
═══════════════════════════════════════════════════════════
{student_prompts_list}

═══════════════════════════════════════════════════════════
FULL CONVERSATION (For context only):
═══════════════════════════════════════════════════════════
{json.dumps(prompt_chain, indent=2)}

⚠️ REMEMBER: 
- Evaluate ONLY what the student typed (User: lines)
- AI responses are context only

FINAL SUBMISSION (For Context):
\"\"\"{submission}\"\"\"

EVALUATION INSTRUCTIONS:
[Detailed instructions...]

{STRUCTURED_OUTPUT_PROMPT}
"""
```
### 3.5 Information Flow

```
Static Components (Always Same)
├── SYSTEM_PROMPT
└── STRUCTURED_OUTPUT_PROMPT
         ↓
Dynamic Components (Per Evaluation)
├── Domain
├── Assignment prompt
├── Rubric text
├── Student prompts (extracted)
├── Full conversation
└── Final submission
         ↓
Generated Output (Structured)
├── Rubric scores (4)
├── Analysis sections (4)
└── Summary (3 paragraphs)
```

## 4. Future Roadmap

### 4.1 Prompt evaluation
A mechanism is required to evaluate the revision chain prompt for 2 reasons:

1. to confirm it is working correctly
2. to enable changes to be evaluated to see if the are improving the output

### 4.2 Prompt and Rubric refinement

This is an initial prompt and it should be possible to improve the output to produce better results.

Similarly, the rubric used is an initial one and it should be possible to optimise it to produce better results.

### 4.3 Chat history collection

An east way for the student to capture and upload their chat history is required.

### 4.4 Pipeline integration

The Jupyter notebook code needs to be integrated into the pipeline.

The JSON file used as input needs to be standardised so that chat histories from different models can be stored in a standard format for input to the revision chain prompt.
