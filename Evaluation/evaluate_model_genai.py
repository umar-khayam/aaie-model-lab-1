import json
import nltk
import torch
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from rouge_score import rouge_scorer
from transformers import AutoTokenizer, AutoModelForCausalLM
from bert_score import score as bert_score_fn
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import (accuracy_score, precision_score, recall_score, f1_score,  confusion_matrix, classification_report)
from transformers import GPT2LMHeadModel, GPT2TokenizerFast, Trainer, TrainingArguments
from transformers import TextDataset, DataCollatorForLanguageModeling
#import streamlit as st
import json

"""#1. EvaluateModel

## i. Dataset Structure Instruction
### a. Classification Model Evaluation
dataset = {

    "text": ["", "", "", ...], #List of the text,
    "labels": ["AI", "Human", "neutral", ...],  # Ground-truth labels (can be int or str)
    "predictions": ["positive", "positive", "neutral", ...]  # Predicted labels (same format as `label`)
}

We can evaluate the model as
```
evaluator = EvaluateModel(dataset=dataset)
evaluator.evaluate_classification_model(average='macro',print_result)
```
The function already support label encoding automatically if your labels are strings.


### b. Generative Model Evaluation

```
dataset = {
    "text": [
        ["The cat sat on the mat.", "A cat is sitting on a mat."],
        ["Hello, how are you?"]
        # Each item is a list of reference texts
    ],
    "generated_texts": [
        "The cat is sitting on the mat.",
        "Hi, how do you do?"
        # Each item is a generated hypothesis
    ]
}
```
We can evaluate the model as


```
evaluator = EvaluateModel(dataset=dataset)
evaluator.evaluate_generative_model(metrics=['bleu', 'rouge', 'bertscore'], print_result=True) # Head to the functio to see more detail
```
"""
default_prompt = """
Decide whether the following text was written by a human or an AI.

Text: "Artificial intelligence is a powerful tool for automating tasks."
Label: AI

Text: "I walked to the market this morning and bought fresh bread."
Label: Human

Text: "The moon is a celestial body that orbits Earth."
Label: AI

Text: "Yesterday, I enjoyed a long walk in the park."
Label: Human

Text: "Machine learning models improve with more data."
Label: AI

Text: {}
Label: Human or AI
"""


class EvaluateModel():
    def __init__(self, dataset=None, model=None, tokenizer=None, model_type = None,few_shot_prompt=None, device=None) -> None:
      self.model = model
      self.tokenizer = tokenizer 
      self.results = {}
      self.device = ("cuda" if torch.cuda.is_available()
                    else "mps" if torch.backends.mps.is_available()
                    else "cpu") if device == "automap" else device
      self.model_type = model_type
      self.dataset = dataset
      self.few_shot_prompt = default_prompt if few_shot_prompt is None else few_shot_prompt
      self.GENAI_PROMPT_PATH = "genai_prompt.json"
    #Check the labels is int and encode it if it is string
    def encode_labels(self, col):
        try:
            int_labels = [int(x) for x in self.dataset[col]]
            label_names = sorted(set(int_labels))
        except ValueError:
            le = LabelEncoder()
            encoded_labels = le.fit_transform(self.dataset[col])
            int_labels = encoded_labels
            label_names = sorted(set(encoded_labels))  # integer labels only

            print(f"The {col} labels have been encoded. Integer mapping:")
            for original, encoded in zip(le.classes_, le.transform(le.classes_)):
                print(f"{original} -> {encoded}")

        return int_labels, label_names

    #Compute the BLEU score
    def bleu_score(self, reference_texts, generated_text):
        ref_tokens = [ref.split() for ref in reference_texts]
        gen_tokens = generated_text.split()
        smoothie = SmoothingFunction().method1
        bleu = sentence_bleu(ref_tokens, gen_tokens, smoothing_function=smoothie)
        return {'bleu': bleu}

    #Compute the ROUGE score
    def rouge_score(self, reference_texts, generated_text):
        scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
        scores = [scorer.score(ref, generated_text) for ref in reference_texts]
        avg_scores = {
            k: np.mean([s[k].fmeasure for s in scores]) for k in scores[0]
        }
        return avg_scores

    #Compute the BERTScore
    def bert_score(self, reference_texts, generated_text, model_type_ = 'bert-base-uncased'):
        P, R, F1 = bert_score_fn([generated_text], [reference_texts], model_type=model_type_)
        return {
            'bertscore_precision': P.mean().item(),
            'bertscore_recall': R.mean().item(),
            'bertscore_f1': F1.mean().item()
        }
    def visualize_attention_heatmap(self, text, print_result = False):
        # ---- Build prompt ----
        prompt = self.few_shot_prompt.format(text)
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
        # ---- Step 1: Get attentions for visualization ----
        outputs = self.model(**inputs, output_attentions=True, return_dict=True)
        attentions = outputs.attentions
        tokens = self.tokenizer.convert_ids_to_tokens(inputs["input_ids"][0])
        # ---- Find classification text segment ----
        text_tokens = self.tokenizer.tokenize(text)

        def normalize_token(t):
            # strip leading Ġ if present
            if t.startswith('Ġ'):
                return t[1:]
            return t

        text_norm = [normalize_token(t) for t in text_tokens]

        for i in range(len(tokens)):
            slice_norm = [normalize_token(t) for t in tokens[i:i+len(text_tokens)]]
            if slice_norm == text_norm:
                start_idx = i
                end_idx = i + len(text_norm)
                break
        else:
            raise ValueError("Could not find text tokens in full prompt tokens")

        # ---- Slice attention to only that segment ----
        attn = attentions[0][0, 0].detach().cpu()
        attn_segment = attn[start_idx:end_idx, start_idx:end_idx]
        tokens_segment = tokens[start_idx:end_idx]

        # ---- Plot ----
        if print_result:
            fig, ax = plt.subplots(figsize=(6, 6))
            cax = ax.matshow(attn_segment, cmap='viridis')
            plt.xticks(range(len(tokens_segment)), tokens_segment, rotation=90)
            plt.yticks(range(len(tokens_segment)), tokens_segment)
            fig.colorbar(cax)
            plt.title("Attention for classification text segment")
            plt.show()

        return attn_segment, tokens_segment
        
    #Evaluate the clasification model
    def evaluate_classification_model(self, average='macro', print_result=False):
        """
        Evaluate a classification model using standard metrics:
        - Accuracy, Precision, Recall, F1-score, Confusion Matrix

        Args:
            average (str): Averaging method for multi-class ('binary', 'micro', 'macro').
            print_result (bool): Whether to print results and plot confusion matrix.

        Workflow:
            - Checks for 'label' and 'prediction' keys in dataset.
            - Encodes non-integer labels if necessary.
            - Computes classification metrics.
            - Optionally prints a classification report and confusion matrix.
        """
        if any(k not in self.dataset for k in ["labels", "predictions"]):
            print("Please provide the dataset with 'label' and 'prediction' columns.")
            return
        # Encode labels (handles string → int mapping if needed)
        targets, label_names_target = self.encode_labels("labels")
        predictions, label_names_prediction = self.encode_labels("predictions")

        label_names = label_names_target

        # Compute evaluation metrics
        acc = accuracy_score(targets, predictions)
        prec = precision_score(targets, predictions, average=average, zero_division=0)
        rec = recall_score(targets, predictions, average=average, zero_division=0)
        f1 = f1_score(targets, predictions, average=average, zero_division=0)
        cm = confusion_matrix(targets, predictions, labels=label_names)

        # Optionally print results
        if print_result:
            plt.figure(figsize=(6, 5))
            sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=label_names, yticklabels=label_names)
            plt.xlabel('Predicted')
            plt.ylabel('Actual')
            plt.title('Confusion Matrix')
            plt.show()

            print(f"Accuracy: {acc:.4f}")
            print(f"F1-score: {f1:.4f}")
            print(f"Recall: {rec:.4f}")
            print(f"Precision: {prec:.4f}")
            print("\nClassification Report:")
            print(classification_report(targets, predictions, labels=label_names, zero_division=0))

        # Store results
        self.results.update({
            "accuracy": acc,
            "precision": prec,
            "recall": rec,
            "f1_score": f1,
        })

    def evaluate_generative_model(self, metrics=['bleu', 'rouge', 'bertscore'], print_result = True, bert_model='bert-base-uncased'):
        """
        Evaluate a generative model using metrics like BLEU, ROUGE, and BERTScore.

        Args:
            metrics (list): List of metrics to compute. Options: 'bleu', 'rouge', 'bertscore'.
            bert_model (str): Hugging Face model name to use for BERTScore.

        Workflow:
            - Validates that 'reference_texts' and 'generated_texts' are in the dataset.
            - Loops over each pair of reference and generated text.
            - Computes and stores selected metrics.
        """
        if "reference_texts" not in self.dataset or "generated_texts" not in self.dataset:
            print("Please provide 'reference_texts' and 'generated_texts' in the dataset.")
            return

        refs = self.dataset['text'].copy()
        gens = self.dataset['generated_texts'].copy()

        for ref, gen in zip(refs, gens):
            # Expect `ref` to be a list of strings, `gen` to be a single string
            if 'bleu' in metrics:
                self.results.update(self.bleu_score(ref, gen))
            if 'rouge' in metrics:
                self.results.update(self.rouge_score(ref, gen))
            if 'bertscore' in metrics:
                self.results.update(self.bert_score(ref, gen, bert_model))

        if print_result:
            print("Generative Model Evaluation Results:")
            for metric, score in self.results.items():
                print(f"{metric:20}: {score:.4f}")

    def load_input_structure(self, **kwargs):
        if self.model_type == "feedback_generation":
            return f'''
            "text": "{kwargs.get("text")}",
            "domain": "{kwargs.get("domain")}",
            "criteria": "{kwargs.get("criteria")}"
            '''
            
        if self.model_type == "ai_detection":
            return f'''
            "text": "{kwargs.get("text")}",
            "label": "{kwargs.get("label")}",
            "prediction": "{kwargs.get("prediction")}"
            '''

    def construct_prompt(self, text, **kwargs):
        with open(self.GENAI_PROMPT_PATH, "r") as f:
            file = json.load(f)

        data = file[self.model_type]

        # Input structure
        if self.model_type == "feedback_generation":
            input_structure = self.load_input_structure(
                text=text,
                domain=kwargs.get("domain"),
                criteria=kwargs.get("criteria")
            )
        elif self.model_type == "ai_detection":
            input_structure = self.load_input_structure(
                text=text,
                label=kwargs.get("label"),
                prediction=kwargs.get("prediction")
            )

        # Criteria
        criteria = ""
        for criterion, values in data["criteria"].items():
            criteria += f"- {criterion}: {values}\n\n"

        # Output structure
        output_structure = ""
        for d, values in data["output_structure"].items():
            if d != "Reasoning":
                output_structure += f"  {d}: {values}\n"
            else:
                output_structure += "  Reasoning:\n"
                for crit, reason in values.items():
                    output_structure += f"    - {crit}: {reason}\n"

        # Example
        example_str = "Example Input:\n"
        for key, value in data["example1"]["input"].items():
            example_str += f"  {key}: {value}\n"

        example_str += "\nExample Output:\n"
        for key, value in data["example1"]["output"].items():
            if key != "Reasoning":
                example_str += f"  {key}: {value}\n"
            else:
                example_str += "  Reasoning:\n"
                for crit, reason in value.items():
                    example_str += f"    - {crit}: {reason}\n"
        #Input key
        input_key = ""
        for key,value in data["example1"]["input"].items():
            input_key += f" - {key} \n"
        # Prompt
        prompt = f"""
            Given that {data["system"]} You must strictly follow the criteria provided and always explain your reasoning based on these set of criteria.
            {criteria}
            Using these input structure {input_key}
            And create a structured output as follows:
            {output_structure}
            Based on this example
            {example_str}
        """
       # print(prompt)
        return prompt, input_structure
        
    def model_based_evaluation(self, file_path=None):
        def generate_result(row):
            print(row)
            kwargs = {}
            if self.model_type == "feedback_generation":
                kwargs["domain"] = row.get("domain")
                kwargs["criteria"] = row.get("criteria")
            elif self.model_type == "ai_detection":
                kwargs["label"] = row["labels"]
                kwargs["prediction"] = row["predictions"]
            else:
                raise ValueError(f"Unknown model_type: {self.model_type}")
    
            sys_prompt, user_prompt = self.construct_prompt(row["text"], **kwargs)
            messages = [
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": user_prompt}
            ]
            inputs = tokenizer.apply_chat_template(
                messages,
                add_generation_prompt=True,
                tokenize=True,
                return_dict=True,
                return_tensors="pt",
            ).to(self.device)
            output_ids = self.model.generate(**inputs, max_new_tokens=400)
            generated_text = self.tokenizer.decode(output_ids[0], skip_special_tokens=True)
            prompt_text = self.tokenizer.decode(inputs["input_ids"][0], skip_special_tokens=True)
            return generated_text[len(prompt_text):].strip()

        for _, row in self.dataset.iterrows():
            print(generate_result(row))


#Pipeline to eveluate the model based on the stored dataset
#We noted that for each model the dataset used will be different, we followed these structure for the the model
    #AI Detection will take : {text}, {labels}, {'predictions'} (You can see the example in the test_ai_detection.csv)
    #Feedback generation wil take: {text}, {domain}, {criteria} (See example in the test_feedback_generation.csv)
#In the following example, we use the Mistral-7B model to test the model in order to used this you will need to access to the token of HuggingFace account and login

#The EvaluateModel objective will take these arguement:
    # - model: the model used to evaluate
    # - tokenizer: the tokenizer use with model
    # - dataset: the dataset used to evaluate the model
    # - model_type: this is the model you want to evaluate, there are only two option (eedback_generation/ai_detection)
    # - device: you can set it by yourself (cuda/cpu/mps) or use "automap"

#In order to evaluate the model using GenAI, you can call model_based_evaluation() function

from huggingface_hub import login
model_id = "mistralai/Mistral-7B-Instruct-v0.2"
token = "HF_TOKEN"
login(token=token)


model = AutoModelForCausalLM.from_pretrained(
        model_id,
        torch_dtype=torch.float16,
        device_map="auto"
    )
tokenizer = AutoTokenizer.from_pretrained(model_id)
testset = pd.read_csv("/kaggle/input/test-feedback/Code Review Feedback Examples.csv")
test_val = EvaluateModel(model=model, tokenizer=tokenizer, dataset = testset, model_type="feedback_generation",device = "automap") #feedback_generation/ai_detection 
test_val.model_based_evaluation()




