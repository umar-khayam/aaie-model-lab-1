
# Data Flow Diagram

The Data Flow Diagram (DFD) of the AAIE system illustrates how data moves from input to output through multiple processing stages. The system begins with two main inputs: student essays with rubrics and teacher feedback with rubrics. These inputs are used to train and test the AI detection and feedback generation models.

## 1. AI Detection Flow

- Student essays and associated teacher feedback first undergo a de-identification process to remove any personally identifiable information.
- The de-identified data is then tokenized and passed through an AI model to detect AI-generated content.

## 2. Feedback Generation Flow

- Teacher feedback and rubrics are similarly de-identified and tokenized.
- The tokenized data is processed by a feedback model and a text generator to produce feedback suggestions.

After the models generate outputs, an additional preprocessing step is applied to refine and clean the results. The feedback from the model is then reviewed manually by the teacher, and this reviewed feedback, along with the original rubrics, is re-processed through the feedback generation pipeline to incorporate the teacher’s input.

The final teacher-reviewed feedback, combined with the AI-generated suggestions, is delivered to the student interface. If the student needs to resubmit, the essay goes through the entire process again. Once the submission is finalized, the completed feedback is displayed to the student.
