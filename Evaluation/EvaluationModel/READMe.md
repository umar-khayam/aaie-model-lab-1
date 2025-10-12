# Model Evaluation Dashboard

A comprehensive Streamlit-based dashboard for evaluating and analyzing machine learning models, specifically designed for AI detection and feedback generation tasks. This tool supports both local HuggingFace models and cloud-based API models with advanced visualization capabilities.

## Features

### Model Support
- **Local HuggingFace Models**: Mistral-7B, Phi-2, Llama-2-7B-Chat
- **API-based Models**: Google Gemini (1.5-Flash, 1.5-Pro), OpenAI GPT-3.5-Turbo
- **Automatic Device Detection**: CUDA/CPU optimization for local models

### Evaluation Types
- **AI Detection**: Classification tasks with accuracy, precision, recall, F1-score metrics
- **Feedback Generation**: Generative tasks with BLEU, ROUGE, BERTScore metrics

### Visualization Features
- **Confusion Matrix**: Interactive heatmaps for classification results
- **Metrics Comparison**: Bar charts for generative model performance
- **Attention Visualization** (Local Models Only):
  - Attention Rollout: Token-level attention importance
  - Attention Weights Heatmap: Layer-specific attention patterns
- **Interactive Plotly Charts**: Responsive and exportable visualizations

### Data Management
- **CSV Upload**: Drag-and-drop file upload interface
- **Data Validation**: Automatic column requirement checking
- **Dataset Preview**: Real-time data inspection and statistics

### Response Generation
- **Sample Response Generation**: Test model outputs with custom prompts
- **Multi-provider Support**: Seamless switching between API and local models

## Requirements

### Python Dependencies
```
torch
streamlit
pandas
matplotlib
seaborn
plotly
transformers
google-generativeai
openai
huggingface_hub
scikit-learn
numpy
```

### API Keys (Optional)
- **Google AI Studio**: For Gemini models
- **OpenAI**: For GPT models
- **HuggingFace**: For gated models (Llama, Mistral)


## Data Format Requirements

### For AI Detection Models
Your CSV file should contain:
- `text`: Input text samples
- `labels`: Ground truth labels (0/1 or categorical)
- `predictions`: Model predictions

Example:
```csv
text,labels,predictions
"This is human text",0,0
"AI generated content",1,1
```

### For Feedback Generation Models
Your CSV file should contain:
- `text`: Input text samples
- `domain`: Task domain/category
- `generated_texts`: Model-generated outputs
- `references`: Reference/ground truth texts

Example:
```csv
text,domain,generated_texts,references
"Essay prompt","education","Generated feedback","Reference feedback"
```

##  Usage Guide

### 1. Model Configuration
- Select your desired model from the dropdown menu
- Enter API keys if required (stored securely in session)
- Click "Test Connection" or "Load Model" to initialize

### 2. Data Upload
- Upload your CSV file using the file uploader
- Review the data preview and validation results
- Ensure all required columns are present

### 3. Evaluation Setup
- Choose evaluation type (AI Detection/Feedback Generation)
- Select metrics for analysis
- Configure averaging method for classification tasks

### 4. Run Analysis
- **Run Evaluation**: Generate comprehensive performance metrics
- **Visualize Attention**: Explore model attention patterns (local models only)
- **Generate Responses**: Test model outputs with sample inputs

### 5. Results Interpretation
- View interactive confusion matrices for classification
- Analyze metric comparison charts for generative models
- Export visualizations and results for reporting

##  Configuration

### Available Models
```python
AVAILABLE_MODELS = {
    "gemini-1.5-flash": "Google's Gemini 1.5 Flash model",
    "gemini-1.5-pro": "Google's Gemini 1.5 Pro model", 
    "mistral-7b": "Mistral 7B Instruct model",
    "phi-2": "Microsoft's Phi-2 language model",
    "llama-7b": "Llama 2 7B Chat model",
    "gpt-3.5-turbo": "OpenAI's GPT-3.5 Turbo model"
}
```

### Evaluation Metrics
- **Classification**: accuracy, precision, recall, f1_score
- **Generative**: bleu, rouge, bertscore
