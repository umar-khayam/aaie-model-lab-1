Team Project Week 4 Planning I. Weekly Task Objectives a. Model
Development Team i. Feedback Generation AI with few-shot learning. For
this task, we use few-shot learning approach using OpenAI's ChatGPT API.
Unlike fine-tuning, few-shot learning allows us to guide the model's
behavior by providing a limited number of example input-output pairs
directly in the prompt. An example of this can be presented below:
\[Student Writing\]: The cat run fast. He scared the dog. \[Feedback\]:
Clarity: The message is understandable but there are some problem: -
Grammar: "run" should be "ran". -Vocab: 'He" should be 'it' \[Student
Writing\]: In my opinion, school should start later because students
need more sleep. \[Feedback\]: Clarity: Very clear. Vocab: All used
correct. Grammar: No major issues.

However, for this one, prompt engineering is an essential skill during
the training process, we need to set some clear criteria when creating
prompt for this. There are some relevant criteria that could be used:
Consistency: The answer should be somehow same so that the model can
follow. Context Match: The answer should be provided with clear context
like "Pretend you are an experience tutor who taught unit \[...\] for a
long time. Based on the following rubric and examples then give me the
feedback"  Make the model to understand the rubric. Length Control: The
answer should be concise and straightforward to avoid hallucination.
Domain Match: The answer should match the unit-specific rubric if
needed. ....

\[Optional\] Implement RAG to the model to improve the generation In
this task, RAG retrieves the most relevant rubrics and example feedback
from a knowledge base, then injects that content into the prompt given
to the ChatGPT API to guide its generation. For this our model could •
Knows what to assess using rubric dataset • Using example to understand
the feedback. • Produces better-structured, rubric-based feedback.

ii. AI content Detection by performing few shot learning This is a
    classification task, so the way to perform few-shot learning might
    be different to achieve the most power of the model. To do this, we
    can adapt few-shot learning strategies from image classification
    that have been trained using meta-learning principles. In
    particular, few-shot classification problems are typically framed as
    N-way K-shot tasks, where a model must learn to classify among N
    classes using only K examples per class. To solve such tasks,
    meta-learning algorithms are trained not just to solve a single
    classification problem, but to learn how to learn---by leveraging
    experience from a distribution of related tasks. Reference:
    https://data-ai.theodo.com/en/technical-blog/few-shot-image-classification-meta-learning

iii. AI content Detection by finetuning the NanoGPT This will be better
     since building classification model might require a lot of resource
     to achieve the best performance. (Discuss)

```{=html}
<!-- -->
```
b.  Evaluation team In this week, our main task can be sumerised as:

-   Setup the Hypothesis for a Good Model (Based on Research)
-   Implement Evaluation Metrics and Pipeline (Interface Level)

i.  Setup the Hypothesis for a Good Model (Based on Research) Formulate
    clear, research-informed hypotheses that describe what makes a model
    successful for two tasks: AI Detection and Feedback Generation. In
    fact, we will need to follow these steps:

```{=html}
<!-- -->
```
1.  Identify the Key Evaluation Metrics: Based on existing research and
    the specific goals of each task, specify which metrics will be used
    to measure model performance. For example: o For AI Detection:
    accuracy, precision, recall, F1-score, AUC-ROC. o For Feedback
    Generation: BLEU, ROUGE, METEOR, human evaluation scores, rubric
    alignment.
2.  Define Success Criteria: Set specific thresholds or target outcomes
    on these metrics that your model should meet or exceed to be
    considered successful. For example: o AI Detection model achieves at
    least 90% F1-score on a balanced test set. o Feedback Generation
    model obtains a BLEU score above 0.35 and passes human rubric
    evaluations with an average rating above 4 out of 5. o Should be
    care about true negative or false positive and the recall or the
    precision. In this task, we will mainly answer two questions:
3.  What evaluation metrics you will use, based on research and task
    relevance
4.  What thresholds or outcomes on those metrics define a "successful"
    model

```{=html}
<!-- -->
```
ii. Implement Evaluation Metrics and Pipeline (Interface Level) In this
    task, our work can be divided to these stuff:

-   Decided the evaluation dataset structure
-   Writing the code for each evaluation metric.
-   Comparing the generated feedback with the rubric to ensure it
    matched.
-   Create a pipeline to evaluate for each model.
