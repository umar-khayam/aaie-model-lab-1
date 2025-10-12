from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report
from ultis.datahandle import DatasetHandler
from ultis.generative_metric import GenerativeMetrics
from ultis.promptbuilder import PromptBuilder
from ultis.attetion_explain import AttentionRollout, AttentionWeight 
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns
import torch 
class EvaluateModel:
    """
    A class to evaluate both classification and generative AI models.
    Provides evaluation metrics, visualization of attention, and prompt construction.
    """

    def __init__(self, dataset, model_type, model=None, tokenizer=None):
        """
        Initialize the evaluation pipeline.

        Args:
            dataset (str or pd.DataFrame): Path or object containing dataset.
            model_type (str): Type of model ('classification', 'feedback_generation', 'ai_detection').
            model (nn.Module/transformers.Model, optional): Model to evaluate (if needed for attention visualization).
            tokenizer (transformers.Tokenizer, optional): Tokenizer for NLP models.
            device (str, optional): Device to run model computations on.
        """
        self.dataset_handler = DatasetHandler(dataset, model_type)  # Handles dataset loading and encoding
        self.metric_evaluator = GenerativeMetrics()                # Computes metrics for generative models
        self.prompt_builder = PromptBuilder(model_type)            # Constructs prompts for generative tasks
        self.model_type = model_type
        self.dataset_prompt = []                                   # Stores constructed system/user messages
        self.results = {}                                          # Stores evaluation results
        self.device = torch.device(
                "cuda" if torch.cuda.is_available() else
                "mps" if torch.backends.mps.is_available() else
                "cpu"
)
    # ----------------------------
    # Evaluate Methods
    # ----------------------------
    def evaluate_classification_model(self, average='macro', print_result=True):
        """
        Evaluate a classification model using standard metrics.

        Args:
            average (str): Method to compute precision/recall/f1 for multi-class ('macro', 'micro', etc.).
            print_result (bool): Whether to print the confusion matrix and classification report.
        """
        # Extract texts, labels, and predictions from dataset
        texts, labels, preds = zip(*self.dataset_handler.iter_classification())

        # Encode labels and predictions into numerical form for metrics computation
        targets, _ = self.dataset_handler.encode_labels("labels")
        predictions, _ = self.dataset_handler.encode_labels("predictions")

        # Compute standard classification metrics
        acc = accuracy_score(targets, predictions)
        prec = precision_score(targets, predictions, average=average, zero_division=0)
        rec = recall_score(targets, predictions, average=average, zero_division=0)
        f1 = f1_score(targets, predictions, average=average, zero_division=0)
        cm = confusion_matrix(targets, predictions)

        # Optional visualization
        if print_result:
            plt.figure(figsize=(6,5))
            sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
            plt.xlabel('Predicted')
            plt.ylabel('Actual')
            plt.show()
            print(classification_report(targets, predictions, zero_division=0))

        # Store results
        self.results.update({"accuracy": acc, "precision": prec, "recall": rec, "f1_score": f1})

    def evaluate_generative_model(self, metrics=['bleu','rouge','bertscore'], print_result=True):
        """
        Evaluate a generative model using selected metrics.

        Args:
            metrics (list of str): Metrics to compute (e.g., BLEU, ROUGE, BERTScore).
            print_result (bool): Whether to print metric results.
        """
        refs, gens = zip(*self.dataset_handler.iter_generative())  # Get references and generated outputs
        print(refs)
        print(gens)
        self.results = self.metric_evaluator.compute_metrics(metrics, refs, gens)
        if print_result:
            for k,v in self.results.items():
                print(f"{k:20}: {v:.4f}")

    def construct_data_messages(self):
        """
        Build system/user messages for all dataset rows using PromptBuilder.
        Useful for generative or AI detection tasks.
        """
        for row in self.dataset_handler.iter_rows():
            kwargs = {}
            kwargs["text"] = row["text"]

            # Add additional fields depending on the model type
            if self.model_type == "feedback_generation":
                kwargs["domain"] = row.get("domain")
                kwargs["generated_texts"] = row.get("generated_texts")
            elif self.model_type == "ai_detection":
                kwargs["label"] = row["labels"]
                kwargs["prediction"] = row["predictions"]
            else:
                raise ValueError(f"Unknown model_type: {self.model_type}")

            # Generate prompts
            s_prompt, u_prompt = self.prompt_builder.construct_prompt(**kwargs)

            # Store as dict for later usage
            messages = {
                "system": s_prompt,
                "user": u_prompt
            }
            self.dataset_prompt.append(messages)
    
    # ----------------------------
    # Visualization Methods
    # ----------------------------
    def visualize_rollout(self, model, tokenizer, text, prompt, title="Attention Rollout", plot=True):
        """
        Visualize attention rollout as a vertical bar chart.
        Tokens on x-axis, attention values on y-axis. Higher attention = taller bars & darker color.
        """
        attn_rollout = AttentionRollout(tokenizer, model, device=self.device)
        token_attention, tokens_segment = attn_rollout(text, prompt)

        attn_values = token_attention.detach().cpu().numpy()

        print("Tokens segment:", tokens_segment)
        print("Attention vector:", attn_values)

        # Normalize colors for intensity
        colors = plt.cm.Reds(attn_values / attn_values.max())
        if plot:
            plt.figure(figsize=(max(6, len(tokens_segment)*0.6), 4))
            plt.bar(tokens_segment, attn_values, color=colors, edgecolor='k', width=0.6)
            plt.ylabel("Attention Value")
            plt.xlabel("Tokens")
            plt.title(title)
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            plt.show()
        return attn_values, token_attention

    def visualize_attention_weights(self, model, tokenizer, text, prompt, title="Attention Weights", plot = True):
        """
        Visualize the attention weights matrix as a heatmap for the text segment.
        Args:
            attn_segment (tensor): attention matrix from AttentionWeight (seq_len, seq_len)
            tokens_segment (list): list of tokens in the text segment
        """
        # Initialize AttentionWeight
        attn_weight = AttentionWeight(tokenizer, model, device= self.device)  # or "cuda"
        
        # Compute attention from layer 2, head 0
        attn_segment, tokens_segment = attn_weight.get_attention_weights(text, prompt, layer=2, head=0)
        if plot:
            plt.figure(figsize=(6, 6))
            sns.heatmap(attn_segment.detach().cpu(), annot=True, cmap='viridis',
                        xticklabels=tokens_segment, yticklabels=tokens_segment)
            plt.title(title)
            plt.xlabel("Tokens (to)")
            plt.ylabel("Tokens (from)")
            plt.show()
        return attn_segment, tokens_segment
