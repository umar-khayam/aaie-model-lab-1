"""Model evaluation utilities.

This module contains the `EvaluateModel` class which can be used to
evaluate classification and generative models on custom datasets. It
encapsulates common metrics such as accuracy, precision, recall and
F1 for classification tasks, as well as BLEU, ROUGE and BERTScore for
generative tasks. The implementation is adapted from the LLM team's
evaluation pipeline and integrated into this codebase for potential
offline analysis.

Typical usage::

    from app.services.evaluation import EvaluateModel
    import pandas as pd

    # classification example
    data = pd.DataFrame({
        'text': ['example 1', 'example 2'],
        'labels': ['AI', 'Human'],
        'predictions': ['AI', 'AI']
    })
    evaluator = EvaluateModel(dataset=data, model_type="ai_detection")
    evaluator.evaluate_classification_model(print_result=True)

    # generative example
    data = {
        'text': [['The cat sat on the mat.'], ['Hello there']],
        'generated_texts': ['A cat is on the mat.', 'Hi']
    }
    evaluator = EvaluateModel(dataset=data, model_type="feedback_generation")
    evaluator.evaluate_generative_model(print_result=True)

Note that these evaluation utilities are not invoked by the FastAPI
endpoints directly but are provided for use by the LLM team or
researchers who wish to benchmark their models locally.
"""

from __future__ import annotations

import json
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Any, Dict, List, Optional
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report,
)

# optional imports; models or tokenizers may not be available in all environments
try:
    from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction  # type: ignore
except Exception:
    sentence_bleu = None  # type: ignore
    SmoothingFunction = None  # type: ignore

try:
    from rouge_score import rouge_scorer  # type: ignore
except Exception:
    rouge_scorer = None  # type: ignore

try:
    from bert_score import score as bert_score_fn  # type: ignore
except Exception:
    bert_score_fn = None  # type: ignore


class EvaluateModel:
    """
    A utility class for evaluating classification and generative models.

    Parameters
    ----------
    dataset : Optional[Dict[str, Any] | pd.DataFrame]
        The dataset to evaluate. For classification tasks, this should
        contain ``'text'``, ``'labels'`` and ``'predictions'``. For
        generative tasks, provide ``'text'`` (reference texts) and
        ``'generated_texts'`` (model outputs).
    model : Any, optional
        A generative model for model‑based evaluation (currently unused).
    tokenizer : Any, optional
        A tokenizer aligned with the provided model (currently unused).
    model_type : Optional[str], optional
        Specifies the type of model being evaluated. Accepted values are
        ``'feedback_generation'`` or ``'ai_detection'``.
    device : Optional[str], optional
        Device specifier for model‑based evaluation (currently unused).

    Notes
    -----
    This class is standalone and does not integrate with the FastAPI
    service. It is provided to mirror the functionality of the LLM
    team's offline evaluation pipeline and can be invoked manually by
    developers.
    """

    def __init__(
        self,
        dataset: Optional[Any] = None,
        model: Optional[Any] = None,
        tokenizer: Optional[Any] = None,
        model_type: Optional[str] = None,
        few_shot_prompt: Optional[str] = None,
        device: Optional[str] = None,
        subscription_key: Optional[str] = None,
        endpoint: Optional[str] = None,
    ) -> None:
        self.model = model
        self.tokenizer = tokenizer
        self.results: Dict[str, Any] = {}
        self.device = device
        self.model_type = model_type
        self.dataset = dataset
        self.few_shot_prompt = few_shot_prompt
        self.subscription_key = subscription_key
        self.endpoint = endpoint
        # if a pandas DataFrame is provided, convert to dict for consistency
        if isinstance(self.dataset, pd.DataFrame):
            self.dataset = self.dataset.to_dict(orient="list")

    def encode_labels(self, col: str) -> (List[int], List[int]):
        """
        Encode string labels into integers automatically.

        Parameters
        ----------
        col : str
            The column name in the dataset containing labels.

        Returns
        -------
        Tuple[List[int], List[int]]
            A tuple of encoded labels and the unique label names as integers.
        """
        try:
            int_labels = [int(x) for x in self.dataset[col]]
            label_names = sorted(set(int_labels))
        except Exception:
            le = LabelEncoder()
            encoded_labels = le.fit_transform(self.dataset[col])
            int_labels = encoded_labels.tolist()
            label_names = sorted(set(encoded_labels))
        return int_labels, label_names

    def bleu_score(self, reference_texts: List[str], generated_text: str) -> Dict[str, float]:
        """Compute the BLEU score for a single generated text against references."""
        if sentence_bleu is None:
            raise RuntimeError("nltk is required for BLEU score but is not available.")
        ref_tokens = [ref.split() for ref in reference_texts]
        gen_tokens = generated_text.split()
        smoothie = SmoothingFunction().method1  # type: ignore
        bleu = sentence_bleu(ref_tokens, gen_tokens, smoothing_function=smoothie)  # type: ignore
        return {"bleu": bleu}

    def rouge_score(self, reference_texts: List[str], generated_text: str) -> Dict[str, float]:
        """Compute the average ROUGE scores for a generated text."""
        if rouge_scorer is None:
            raise RuntimeError("rouge_score is required for ROUGE but is not available.")
        scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)  # type: ignore
        scores = [scorer.score(ref, generated_text) for ref in reference_texts]  # type: ignore
        avg_scores = {k: np.mean([s[k].fmeasure for s in scores]) for k in scores[0]}  # type: ignore
        return avg_scores

    def bert_score(self, reference_texts: List[str], generated_text: str, model_type_: str = 'bert-base-uncased') -> Dict[str, float]:
        """Compute BERTScore for a generated text."""
        if bert_score_fn is None:
            raise RuntimeError("bert-score is required for BERTScore but is not available.")
        P, R, F1 = bert_score_fn([generated_text], [reference_texts], model_type=model_type_)  # type: ignore
        return {
            'bertscore_precision': P.mean().item(),
            'bertscore_recall': R.mean().item(),
            'bertscore_f1': F1.mean().item(),
        }

    def evaluate_classification_model(self, average: str = 'macro', print_result: bool = False) -> None:
        """
        Evaluate a classification model using standard metrics.

        The dataset must contain ``'labels'`` and ``'predictions'`` keys.

        Parameters
        ----------
        average : str, optional
            Averaging method for multi‑class metrics (``'binary'``, ``'micro'``, ``'macro'``), by default 'macro'.
        print_result : bool, optional
            Whether to print results and plot the confusion matrix.
        """
        if not self.dataset or any(k not in self.dataset for k in ['labels', 'predictions']):
            print("Please provide the dataset with 'labels' and 'predictions' columns.")
            return
        targets, label_names_target = self.encode_labels('labels')
        predictions, _ = self.encode_labels('predictions')
        label_names = label_names_target
        acc = accuracy_score(targets, predictions)
        prec = precision_score(targets, predictions, average=average, zero_division=0)
        rec = recall_score(targets, predictions, average=average, zero_division=0)
        f1 = f1_score(targets, predictions, average=average, zero_division=0)
        cm = confusion_matrix(targets, predictions, labels=label_names)
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
        self.results.update({
            'accuracy': acc,
            'precision': prec,
            'recall': rec,
            'f1_score': f1,
        })

    def evaluate_generative_model(self, metrics: Optional[List[str]] = None, print_result: bool = True, bert_model: str = 'bert-base-uncased') -> None:
        """
        Evaluate a generative model using BLEU, ROUGE and BERTScore.

        The dataset must contain ``'text'`` (reference texts) and
        ``'generated_texts'`` (hypotheses).

        Parameters
        ----------
        metrics : list of str, optional
            Metrics to compute (any of ``'bleu'``, ``'rouge'``, ``'bertscore'``), by default all.
        print_result : bool, optional
            Whether to print the results.
        bert_model : str, optional
            Name of the Hugging Face model to use for BERTScore.
        """
        if not metrics:
            metrics = ['bleu', 'rouge', 'bertscore']
        if not self.dataset or 'text' not in self.dataset or 'generated_texts' not in self.dataset:
            print("Please provide 'text' and 'generated_texts' in the dataset.")
            return
        refs = self.dataset['text']
        gens = self.dataset['generated_texts']
        for ref, gen in zip(refs, gens):
            if 'bleu' in metrics:
                try:
                    self.results.update(self.bleu_score(ref, gen))
                except Exception:
                    pass
            if 'rouge' in metrics:
                try:
                    self.results.update(self.rouge_score(ref, gen))
                except Exception:
                    pass
            if 'bertscore' in metrics:
                try:
                    self.results.update(self.bert_score(ref, gen, bert_model))
                except Exception:
                    pass
        if print_result:
            print("Generative Model Evaluation Results:")
            for metric, score in self.results.items():
                if isinstance(score, float):
                    print(f"{metric:20}: {score:.4f}")
                else:
                    print(f"{metric:20}: {score}")

# ---------------------------------------------------------------------------
# Additional helpers for feedback generation metrics and post-processing

def list_to_paragraph(value: Any) -> str:
    """
    Convert a list or bullet-marked string into a single cohesive paragraph.

    Many language model outputs contain lists (either as Python lists or
    newline‑delimited strings beginning with bullets such as '-', '*', '•'
    or numbered lines like '1.', '2)', etc.). This helper flattens those
    structures into a single paragraph of text. If the input is already
    a string without bullets, it is returned with normalised whitespace.

    Parameters
    ----------
    value : Any
        The value to normalise. It may be a list, string or other type.

    Returns
    -------
    str
        A single paragraph with bullet markers removed and sentences
        punctuated appropriately.
    """
    # Lists: join elements into sentences.
    if isinstance(value, list):
        parts: List[str] = []
        for item in value:
            if not isinstance(item, str):
                continue
            txt = item.strip().rstrip(';,.')
            if not txt:
                continue
            parts.append(txt)
        # Join with period and space
        if not parts:
            return ""
        paragraph = '. '.join(parts)
        if not paragraph.endswith('.'):
            paragraph += '.'
        return paragraph
    # Strings: normalise whitespace and strip bullet markers
    if isinstance(value, str):
        # split into lines
        lines = value.splitlines()
        cleaned: List[str] = []
        for line in lines:
            s = line.strip()
            if not s:
                continue
            # remove bullet or numbering prefixes
            s = re.sub(r'^\s*([-*•]+\s+)', '', s)
            s = re.sub(r'^\s*(\d+)[\).]\s+', '', s)
            cleaned.append(s)
        if not cleaned:
            return ""
        paragraph = ' '.join(cleaned)
        paragraph = re.sub(r'\s+', ' ', paragraph).strip()
        # ensure a terminal period
        if paragraph and paragraph[-1] not in '.?!':
            paragraph += '.'
        return paragraph
    # Fallback: cast to string
    return str(value)

def analyze_raw_feedback_output(raw_text: str) -> Dict[str, Any]:
    """
    Analyse the raw language model output for feedback before JSON parsing.

    This function computes simple metrics about the formatting of the raw
    string returned from the LLM. It checks whether a JSON object appears
    in the text, counts the number of lines and lines beginning with a
    typical bullet marker or enumeration, estimates the density of bullet
    lines, and reports character and approximate sentence counts. The
    metrics are printed to standard output with a `[evaluation]` prefix.

    Parameters
    ----------
    raw_text : str
        The unparsed output from the language model.

    Returns
    -------
    Dict[str, Any]
        A dictionary of computed metrics. The keys include:
        ``has_json_object``, ``lines``, ``bulleted_lines``,
        ``bullet_density_pct``, ``char_count`` and ``approx_sentence_count``.
    """
    if raw_text is None:
        raw_text = ""
    # Determine if the output contains a JSON object (simple heuristic)
    has_json = bool(re.search(r'\{.+\}', raw_text, flags=re.S))
    lines = raw_text.splitlines()
    num_lines = len(lines)
    bullet_lines = 0
    for ln in lines:
        stripped = ln.lstrip()
        if not stripped:
            continue
        # bullet markers: '-', '*', '•', numeric enumerations (1., 1), etc.
        if stripped.startswith(('-', '*', '•')):
            bullet_lines += 1
            continue
        if re.match(r'\d+[\).]', stripped):
            bullet_lines += 1
            continue
    bullet_density = (bullet_lines / num_lines * 100) if num_lines else 0.0
    char_count = len(raw_text)
    approx_sentence_count = len(re.findall(r'[.!?]', raw_text))
    # Print metrics to stdout
    print(f"[evaluation] raw.has_json_object: {has_json}")
    print(f"[evaluation] raw.lines: {num_lines} | raw.bulleted_lines: {bullet_lines}")
    print(f"[evaluation] raw.bullet_density_pct: {bullet_density:.1f}")
    print(f"[evaluation] raw.char_count: {char_count}")
    print(f"[evaluation] raw.approx_sentence_count: {approx_sentence_count}")
    return {
        'has_json_object': has_json,
        'lines': num_lines,
        'bulleted_lines': bullet_lines,
        'bullet_density_pct': bullet_density,
        'char_count': char_count,
        'approx_sentence_count': approx_sentence_count,
    }

def log_feedback_metrics(feedback: Dict[str, Any], rubric: Dict[str, Any]) -> None:
    """
    Log simple metrics about a structured feedback object.

    After the feedback has been parsed and normalised into the desired
    structure, this function prints summary statistics to stdout. It
    reports the overall grade, how many rubric criteria were covered
    relative to the rubric supplied, and the length of the reasoning
    field in characters.

    Parameters
    ----------
    feedback : Dict[str, Any]
        The structured feedback dictionary produced by the evaluator.
    rubric : Dict[str, Any]
        The rubric dictionary used to evaluate submissions.
    """
    try:
        overall = feedback.get('overall_grade')
        reason = feedback.get('reasoning', '')
        covered = len(feedback.get('criteria', []))
        expected = len(rubric.get('criteria', []))
        print(f"[evaluation] overall_grade: {overall}")
        print(f"[evaluation] criteria_coverage: {covered}/{expected}")
        print(f"[evaluation] reasoning_length_chars: {len(reason) if isinstance(reason, str) else 0}")
    except Exception:
        # Fallback if keys are missing
        print("[evaluation] Unable to log feedback metrics due to malformed structure.")