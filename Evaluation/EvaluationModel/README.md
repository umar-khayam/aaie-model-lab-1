# Model Evaluation Toolkit


A comprehensive Python toolkit for evaluating both classification and generative models, with specialized support for AI vs Human text classification using few-shot learning approaches.

## 🚀 Features

- **Dual Evaluation Support**: Evaluate both classification and generative models with a unified interface
- **Multiple Metrics**: Support for BLEU, ROUGE, BERTScore for generative models and standard classification metrics
- **Automatic Label Encoding**: Seamlessly handles both string and integer labels
- **Few-shot Learning**: Built-in support for few-shot prompting with customizable templates
- **AI Detection Pipeline**: Complete end-to-end pipeline for AI vs Human text classification
- **Visualization**: Rich plotting capabilities with confusion matrices and detailed reports

## 📦 Installation


```bash
pip install torch transformers nltk rouge-score bert-score scikit-learn matplotlib seaborn pandas numpy streamlit
```

## 🔧 Usage


### 1. Classification Model Evaluation

Perfect for evaluating AI detection models, sentiment analysis, or any classification task.

#### Dataset Structure
```python
dataset = {
    "prompts": ["Text sample 1", "Text sample 2", "Text sample 3"],
    "labels": ["AI", "Human", "AI"],  # Ground-truth labels
    "predictions": ["AI", "Human", "Human"]  # Model predictions
}
```

#### Basic Usage
```python
from evaluate_model import EvaluateModel

# Initialize evaluator
evaluator = EvaluateModel(dataset=dataset)

# Evaluate classification performance
evaluator.evaluate_classification_model(average='macro', print_result=True)
```

#### Features:
- **Automatic Label Encoding**: Handles both string and integer labels automatically
- **Multiple Averaging Methods**: Support for 'binary', 'micro', and 'macro' averaging
- **Rich Visualizations**: Confusion matrix heatmaps and detailed classification reports
- **Comprehensive Metrics**: Accuracy, Precision, Recall, F1-score

### 2. Generative Model Evaluation

Ideal for evaluating text generation, translation, summarization, and other generative tasks.

#### Dataset Structure
```python
dataset = {
    "reference_texts": [
        ["The cat sat on the mat.", "A cat is sitting on a mat."],  # Multiple references
        ["Hello, how are you?"]  # Single reference
    ],
    "generated_texts": [
        "The cat is sitting on the mat.",  # Generated hypothesis
        "Hi, how do you do?"
    ]
}
```

#### Basic Usage
```python
# Initialize evaluator
evaluator = EvaluateModel(dataset=dataset)

# Evaluate with multiple metrics
evaluator.evaluate_generative_model(
    metrics=['bleu', 'rouge', 'bertscore'], 
    print_result=True,
    bert_model='bert-base-uncased'
)
```

#### Supported Metrics:
- **BLEU Score**: Measures n-gram overlap with reference texts
- **ROUGE Scores**: ROUGE-1, ROUGE-2, and ROUGE-L for recall-oriented evaluation
- **BERTScore**: Semantic similarity using contextualized embeddings


### 3. End-to-End AI Detection Pipeline

The toolkit includes a complete pipeline for AI vs Human text classification:

```python
from evaluate_model import process_model

# Prepare your data
data = {
    "prompts": ["List of texts to classify"],
    "labels": ["Known labels for evaluation"]
}

# Process with Phi-2 model (requires ./phi-2 model directory)
data_with_predictions = process_model(data, few_shot_prompt=custom_prompt)

# Evaluate the results
evaluator = EvaluateModel(dataset=data_with_predictions)
evaluator.evaluate_classification_model(print_result=True)
```


## 🎯 Key Improvements in This PR

## Key Improvements in This PR

### 1. **Enhanced Evaluation Framework**
- **Unified Interface**: Single class handles both classification and generative model evaluation
- **Flexible Data Structures**: Supports various input formats and automatically handles preprocessing
- **Comprehensive Metrics**: Industry-standard metrics for both model types

### 2. **Dual Evaluation Functions**


#### Classification Evaluation (`evaluate_classification_model`)
- **Multi-class Support**: Handles binary and multi-class classification
- **Automatic Preprocessing**: Label encoding for string labels
- **Rich Reporting**: Confusion matrices, classification reports, and metric summaries

#### Generative Evaluation (`evaluate_generative_model`)
- **Multiple Reference Support**: Handle multiple reference texts per generated output
- **Diverse Metrics**: BLEU, ROUGE, and BERTScore in a single call
- **Semantic Understanding**: BERTScore for meaning-based evaluation beyond n-gram matching

### 3. **AI Detection Pipeline**
- **Few-shot Learning**: Built-in prompts for AI vs Human text classification
- **Model Integration**: Seamless integration with Hugging Face transformers (Phi-2 example included)
- **End-to-end Processing**: From raw text to evaluation results in a single pipeline

## 📊 Output Examples


### Classification Results
```
Accuracy: 0.8500
F1-score: 0.8421
Recall: 0.8400
Precision: 0.8500

Classification Report:
              precision    recall  f1-score   support
           0       0.85      0.89      0.87        50
           1       0.85      0.80      0.82        40
```

### Generative Results
```
Generative Model Evaluation Results:
bleu                : 0.7234
rouge1              : 0.8123
rouge2              : 0.7456
rougeL              : 0.7890
bertscore_precision : 0.8567
bertscore_recall    : 0.8234
bertscore_f1        : 0.8398
```


## 🔬 Technical Details

- **Device Support**: Automatic GPU/MPS detection for optimal performance
- **Memory Efficient**: Handles large datasets with batched processing
- **Error Handling**: Comprehensive error checking and informative messages
- **Extensible Design**: Easy to add new metrics and evaluation methods

## 🤝 Contributing

This toolkit is designed to be extensible. Feel free to add new metrics, visualization methods, or evaluation approaches by following the established patterns in the codebase.

## 📝 License

[Add your license information here]

---

*This evaluation toolkit provides a comprehensive solution for both classification and generative model assessment, with the added benefit of attention visualization for model interpretability.*
