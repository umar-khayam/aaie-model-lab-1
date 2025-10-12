from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from rouge_score import rouge_scorer
from bert_score import score as bert_score_fn
import numpy as np

class GenerativeMetrics:
    def __init__(self, bert_model='bert-base-uncased'):
        self.bert_model = bert_model
        self.metric_registry = {
            "bleu": self.bleu_score,
            "rouge": self.rouge_score,
            "bertscore": self.bert_score
        }

    def bleu_score(self, reference_texts, generated_text):
        ref_tokens = [ref.split() for ref in reference_texts]
        gen_tokens = generated_text.split()
        smoothie = SmoothingFunction().method1
        return {'bleu': sentence_bleu(ref_tokens, gen_tokens, smoothing_function=smoothie)}

    def rouge_score(self, reference_texts, generated_text):
        scorer = rouge_scorer.RougeScorer(['rouge1','rouge2','rougeL'], use_stemmer=True)
        scores = [scorer.score(ref, generated_text) for ref in reference_texts]
        avg_scores = {k: np.mean([s[k].fmeasure for s in scores]) for k in scores[0]}
        return avg_scores

    def bert_score(self, reference_texts, generated_text):
        P, R, F1 = bert_score_fn([generated_text], [reference_texts], model_type=self.bert_model)
        return {
            'bertscore_precision': P.mean().item(),
            'bertscore_recall': R.mean().item(),
            'bertscore_f1': F1.mean().item()
        }

    def compute_metrics(self, metrics, references, generations):
        all_scores = {m: [] for m in metrics}
        for ref, gen in zip(references, generations):
            for metric in metrics:
                if metric in self.metric_registry:
                    scores = self.metric_registry[metric](ref, gen)
                    for k, v in scores.items():
                        all_scores.setdefault(k, []).append(v)
        # Aggregate
        return {k: np.mean(v) for k,v in all_scores.items()}
