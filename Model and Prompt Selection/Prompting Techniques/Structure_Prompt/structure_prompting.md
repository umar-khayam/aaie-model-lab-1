# Structured Prompting for Feedback Generation and AI Detection

## 1. Introduction

### a. Structure Prompting

Structured prompting is a prompting technique where the input to a large language model (LLM) is crafted in a clear, rule-based, and organized format. Instead of relying on casual or vague instructions, structured prompts are built like a structured framework that guide the model toward a specific, predictable output. In fact, a well-designed structured prompt usually includes the following components:

1. **Clear Instructions:** which clearly state the goal of the task and what the model should produce to help eliminate ambiguity and reduce irrelevant or inconsistent responses. Decompose complex tasks into ordered steps to enforce a logical workflow (e.g., "Step 1: Identify strengths; Step 2: Suggest improvements; Step 3: Rate overall quality"). This prevents free-form, unstructured answers and improves consistency. 
   - *Example*: "Summarize the following article into exactly 3 bullet points, each under 15 words."

2. **Role alignment** used to direct the model to adopt a particular persona, expertise, or perspective to shape the tone, style, and depth of the response. 
   - *Example*: "You are an experienced software engineer. Explain this algorithm as if teaching a beginner."

3. **Constraints** is to define rules and boundaries for the output, such as format, style, or length in order to ensure outputs are consistent, structured, and usable. 
   - *Example*: "Respond in JSON format with keys: 'title', 'summary', and 'keywords'."

4. **Examples or context** to provide sample inputs and outputs, or reference materials, so the model can learn the desired pattern. This was great for complex tasks where simple instructions aren't enough.
   - *Feedback generation example*: include a student answer plus a model feedback sample that follows your rubric and format.
   - *AI detection example*: include labeled samples ("AI-generated" vs "Human-written") with brief rationales, then ask the model to classify a new text and explain its reasoning.

### b. Comparison of different prompting methods

Few-shot prompting involves providing the model with a handful of demonstration examples in-line along with task instructions, allowing it to infer the pattern and apply it to new inputs. For instance, a sentiment analysis task might include two labelled examples of text and sentiment before asking the model to classify a new text. This method is simple to implement and effective when the desired pattern is clear, but its guidance is limited to what the examples illustrate, and too many examples can overwhelm the prompt.

Role-based prompting, on the other hand, assigns the model a specific persona or domain expert role such as a senior legal analyst or a math tutor, which shapes the tone, depth, and vocabulary of the response. This approach is especially useful for domain-specific or tone-sensitive tasks like legal advice, teaching feedback, or marketing copy, though it offers less structural control and may produce shallow or inconsistent outputs if the role is loosely defined.

Structured prompting goes further by combining detailed instructions, role assignment, constraints, and sometimes examples into a rule-based framework that often breaks the task into sub-steps or specifies an explicit output format. While this method requires more effort to design, it ensures consistency, predictability, and repeatability, making it ideal for complex reasoning, data extraction, or high-stakes applications where reliability and auditability are critical.

| Prompting Method | Structure | Typical Use Cases |
|------------------|-----------|------------------|
| Structured | Detailed instructions, role assignment, constraints, sometimes examples; may include sub-steps and output schema. | Complex tasks needing consistency (multi-step reasoning, data extraction, regulated outputs). |
| Few-Shot | Few input–output examples plus task instruction. The model infers the pattern from examples. | General tasks like classification, data extraction, or creative tasks where patterns are clear. |
| Role-Based | Persona or role assignment plus brief task instruction. | Domain-specific or tone-sensitive. |

## 2. RTCSIO Framework

### a. Overview

RTCSIO stands for Role, Task, Constraints, Steps, Input, Output. It is a structured prompting framework that provides clarity, consistency, and reliability for AI tasks. Each component serves a specific purpose in guiding the AI's reasoning and output. In fact, each components in the framework can be described as:

1. **Role(R)**: The Role defines the persona or expertise the AI should assume. Assigning a role is essential because it sets the tone, depth, and perspective of the response.

   For example, asking the model to act as a "senior academic reviewer" ensures that feedback is constructive, professional, and aligned with academic standards. Similarly, assigning a role like "AI text detector" frames the AI to focus on analytical and objective evaluation rather than free-form creative writing.

2. **Task (T)**: The Task explicitly states what the AI is supposed to accomplish. It clarifies the primary goal, preventing ambiguity. Without a clearly defined task, the AI may produce irrelevant or inconsistent outputs.

   For Feedback AI, this could be "Analyze the text and generate detailed feedback." For AI Detection, the task might be "Classify the text as AI-generated or human-written."

3. **Constraints(C)**: Constraints specify rules, limits, or formatting requirements for the output and input. They improve reliability, readability, and reusability. For instance, a JSON ensures machine-readable outputs, and length or style constraints prevent verbose or off-topic answers. Constraints reduce variability and hallucinations, ensuring outputs are aligned with intended standards.

4. **Steps(S)**: Steps provide a logical workflow or reasoning path that the AI should follow. Breaking the task into ordered steps helps the AI reason in a structured manner and ensures no important sub-task is overlooked.

   For feedback generation, this could include steps like identifying strengths, weaknesses, and suggestions. For AI detection, it could involve analyzing structure, checking linguistic patterns, and making a classification.

5. **Input(I)**: The Input component specifies the example data or content the AI will work with. Providing clear input is critical because the model cannot perform the task accurately without understanding the material it is analyzing. This could be a student essay, a code snippet, or a text sample for AI detection.

6. **Output(O)**: The Output defines example for the desired format, structure, and type of the result. A clearly defined output ensures consistency and reproducibility. It can include structured schemas like JSON objects or step-by-step lists.

Following the RTCSIO structure ensures that every aspect of the AI's reasoning and output is guided. The Role and Task provide context and purpose, Constraints enforce rules, Steps guide logical reasoning, Input specifies what to analyze, and Output ensures consistent formatting. This structured approach reduces errors and ambiguity while improving reproducibility.

### b. Prompt Using RTCSIO Framework

#### i. Feedback Generation AI Example

1. **Role:** "You are a helpful and respectful educational assessment assistant that provides feedback on submitted work. Always answer as helpfully as possible, while being safe. Your answers should not include any harmful, unethical, racist, sexist, toxic, dangerous, or illegal content. Provide assessment feedback and a rating for the assessment based on performce descriptors."

2. **Task:** "Analyze the student's response and generate detailed, actionable feedback."

3. **Constraints (Input/Output Structure):**
   - **Input:** text (the student submission)
   - **Output:** plain text only (no JSON, no files), structured as:
     ```
     Overall Summary:
     <2–4 sentence overview of strengths and priorities>
     
     Criteria Feedback:
     Criterion: <criterion_id>
     Rating: excellent | good | average | needs_improvement | poor
     Evidence:
     - point 1
     - point 2
     Improvement Tip: one concrete suggestion
     
     Suggested Grade: <optional short string>
     ```

4. **Steps:**
   - Summarize overall performance in 2-4 sentences.
   - For each rubric criterion:
     - Identify rating (excellent → poor)
     - Provide evidence from the submission (1-3 points)
     - Give one concrete improvement tip

5. **Input:**
   Text: 'The causes of World War I include political alliances, militarism, and nationalism...'
   
   Rubric:
   - Understanding of key concepts
   - Depth of analysis
   - Evidence and examples
   - Clarity and organization

6. **Output:**
   ```
   Overall Summary: The student clearly identifies the main causes of World War I and presents the information in a logical order. However, the analysis is somewhat limited and could benefit from additional context and supporting examples.
   
   Criteria Feedback:
   Criterion: Understanding of key concepts
   Rating: good
   Evidence:
   - Correctly identifies political alliances, militarism, and nationalism
   - Demonstrates basic understanding of causes
   Improvement Tip: Include additional factors such as economic and social causes
   ```

#### ii. AI Detection Example

1. **Role:** "You are an impartial AI text detector evaluating whether a given text is AI- or human-generated."

2. **Task:** "Classify the text and provide reasoning for your decision."

3. **Constraints (Input/Output Structure):**
   - **Input:** {text} must be a single string containing the text sample to classify.
   - **Output:** Must be a JSON object with the following keys:
     - label (string: "AI-generated" or "Human-written")
     - Reasoning:
       - Bullet point 1
       - Bullet point 2

4. **Steps:**
   - Analyze the text's linguistic patterns and style.
   - Compare patterns to typical AI-generated and human-written texts.
   - Determine the label (AI-generated or human-written).
   - Provide reasoning and a confidence score.

5. **Input:**
   "Text: 'The sun rises in the east and sets in the west. It is an observable astronomical phenomenon...'"

6. **Output:**
   ```json
   {
     "label": "AI",
     "Reasoning": "- Uses highly generic phrasing without personal context
                   - Contains repeated sentence structures",
     "confidence": 0.92
   }
   ```

## 3. Performance Report

### a. Human Rating

We focus to examine some example to keep of the model.

**Accounting:**

"Blockchain technology, defined by its decentralization, immutability, and transparency, is transforming traditional accounting practices, particularly in auditing and financial reporting. Its core principles—decentralized ledgers, immutable records, and smart contracts—enable significant improvements in efficiency and trust. Smart contracts automate tasks like invoicing and reconciliation, reducing errors and intermediaries. For auditing, blockchain's immutable records create tamper-proof audit trails, simplifying verification and enhancing fraud detection. Real-time financial reporting becomes feasible as transactions are instantly recorded on a shared ledger, improving transparency and decision-making. For example, Ernst & Young uses its Blockchain Analyzer to audit cryptocurrency transactions, streamlining assurance processes, while JPMorgan's Quorum platform facilitates efficient interbank reconciliations. However, challenges persist. Regulatory uncertainty, such as the lack of clear accounting standards for blockchain assets, complicates compliance. Scalability issues in public blockchains and the high cost of integrating with legacy systems pose barriers, particularly for smaller firms. Additionally, adopting blockchain requires significant technical expertise. Despite these hurdles, blockchain's potential to enhance data integrity and automation signals a transformative shift in accounting, as demonstrated by firms like PwC exploring blockchain-based auditing tools. As technology and regulations evolve, blockchain will likely redefine trust and efficiency in accounting practices."

**True Classification:** AI

**Model Prediction:** AI

**Evaluation Result:** Correct PREDICTION

**Analysis:**
- Overly formal or academic tone in casual contexts
- Perfect grammar and punctuation (too polished)
- Overly formal

### b. GenAI Rating

#### i. AI Detection

| Department | Accuracy |
|------------|----------|
| Accounting | 0.6667   |
| Engineering| 0.5000   |
| IT         | 0.6667   |
| Psychology | 0.5000   |
| Teaching   | 0.3333   |

![AIDection](ai_dection.png)
The confidence distribution reveals that participants were generally quite certain about their responses, with the vast majority (approximately 19 out of 28 responses) given at the highest confidence level of 5, while only a small fraction demonstrated low confidence. However, this high level of confidence did not translate uniformly into accuracy across all departments, suggesting a potential disconnect between perceived and actual performance.

The departmental accuracy analysis shows significant variation in performance, with Accounting and IT departments achieving the highest accuracy rates at 66.67% each, followed by Engineering and Psychology at a moderate 50%, while the Teaching department lagged considerably behind at just 33.33%.

#### ii. Feedback Generation
![feedback_result](feedback_result.png)
The figure shows the results produced by the GenAI model. Overall, the model achieved high scores, indicating it can be reliably reused. The lowest score was 3.83, while the highest reached 5.0. Most predictions clustered around 4.67, with approximately ten instances at this value, and three predictions achieved a perfect score of 5.0.