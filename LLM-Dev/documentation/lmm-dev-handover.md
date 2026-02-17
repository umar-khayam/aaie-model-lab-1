# Frontend Dashboard — LLM Comparison Interface Handover

This document provides a summary of the completed demonstration interface for side-by-side model comparison developed during Sprint 2 for the AAIE LLM-Dev stream.

## IMPORTANT

**Link to custom model:** https://deakin365.sharepoint.com/:f:/r/sites/Deakin-MITHackathon/Shared%20Documents/AAIE%20-%20Artificial%20Assessment%20Intelligence%20for%20Educ/Mini-LLM%20model?csf=1&web=1&e=hySz8T

## System Features

### I. Functional Features

#### 1.1 Comparison Page Interface

Interactive comparison interface for demonstrating zero-shot vs custom model outputs with animated text rendering. Completed features:

- Input field for essay prompts with Enter-key support
- Side-by-side output boxes (Zero-Shot Model vs Custom Model)
- Character-by-character typing animation (30ms per character) to simulate real inference
- "Submit" button to trigger comparison (disables during animation)
- "New Chat" button to reset interface for testing multiple prompts
- Pre-loaded sample responses for 4 test prompts

The comparison page is implemented in `comparison.html` with logic in `app.js`. Responses are stored in a `sampleResponses` object mapping prompt strings to model outputs. The interface supports any length of text output with auto-expanding output boxes.

**Test prompts:**
1. "once upon a time, a small robot decided to"
2. "artificial intelligence will change education by"
3. "explain reinforcement learning in a simple way."
4. "write a short story about a lost dog who finds home."

#### 1.2 Metrics Dashboard

Static metrics display page showing model evaluation results across multiple categories. Implemented displays:

- Content Assessment metrics (Pearson, Spearman, MSE, Kappa)
- Organization Assessment metrics
- Language Assessment metrics
- Overall Performance metrics (including BERT Score, Sample Count, Citation Recall)
- Judge Evaluation metrics (10 categories)

Metrics are defined in `app.js` and rendered dynamically via Bootstrap cards. The page is implemented in `metrics.html` with styling in `styles.css`.

#### 1.3 Navigation Structure

Multi-page dashboard with Bootstrap navbar providing access to:

- Home page (landing/welcome)
- Metrics page (evaluation results)
- Zero-Shot Comparison page (interactive demo)

### II. Technical Implementation

#### 2.1 Frontend Stack

- **HTML5**: Semantic structure for all pages
- **CSS3/Bootstrap 5.3**: Responsive styling and layout components
- **Vanilla JavaScript**: DOM manipulation, event handling, and animation logic
- **No build tools**: Direct browser execution for simplicity

#### 2.2 Data Structure

Sample responses stored as JavaScript object:

```javascript
const sampleResponses = {
    "prompt text": {
        zeroShot: "zero-shot model output",
        custom: "custom model output"
    }
};
```

Metrics stored as nested object structure with categories (content, organization, language, overall, judge).

#### 2.3 Styling

- Purple gradient headers for metric categories
- Monospace font (Courier New) for model outputs
- Auto-expanding output boxes with 300px minimum height
- Responsive grid layout (50/50 split on desktop, stacked on mobile)

## Current Limitations

- **Static demonstration only**: No live model integration, uses pre-generated responses
- **Limited prompt set**: Only 4 hardcoded prompts available for testing
- **No backend connection**: All data is client-side only
- **No user authentication**: Open access to all pages
- **No result persistence**: Outputs disappear on page reload
- **Case-sensitive matching**: Prompts must match exactly (though lowercased internally)

## Model Setup Documentation

### III. Zero-Shot Model Setup

**Model:** Qwen 2.5-3B-Instruct

**Implementation:** Zero-shot baseline for comparison against the custom-trained Mini-LLM. Pretrained instruction-tuned model used in inference-only mode.

#### 3.1 Model Characteristics

- **Model family**: Qwen 2.5
- **Parameter size**: ~2.5 billion parameters
- **Training status**: Fully pretrained and instruction-tuned
- **Usage mode**: Zero-shot inference only
- **Instruction alignment**: Native (Instruct variant)
- **Structured output handling**: Strong (e.g., JSON, lists, formatted responses)

The model weights are provided by the model publisher and are not modified during this project.

#### 3.2 Setup and Configuration

- **Execution mode**: Inference only
- **Deployment**: Local or hosted inference runtime (depending on environment)
- **Prompting**: Zero-shot prompts (no examples provided)
- **Decoding**: Default decoding parameters to ensure deterministic behaviour
- **Context handling**: Supports longer context windows than the custom Mini-LLM

No additional adapters, LoRA layers, or fine-tuning steps are applied.

#### 3.3 Zero-Shot Prompting Strategy

To ensure a fair comparison:

- Identical prompts are used for both the zero-shot model and the custom Mini-LLM
- No task-specific demonstrations or few-shot examples are provided
- Prompts include:
  - Open-ended generation
  - Explanatory questions
  - Technology-related prompts
  - Structured output requests (e.g., JSON)

This isolates the effect of model pretraining and alignment.

#### 3.4 Limitations and Considerations

- Model training data and internal representations are not accessible
- Behaviour cannot be customised without additional fine-tuning
- Performance reflects a general-purpose instruction-aligned model
- Results represent an upper-bound reference, not a deployment target

These factors are considered when interpreting comparative results.

**Comments:**

Qwen 2.5-3B-Instruct is used as a zero-shot baseline representing a modern, instruction-aligned language model. It provides a meaningful point of comparison for assessing the strengths and limitations of the custom-trained Mini-LLM, particularly in instruction following and structured output generation.

### IV. Custom Model Training

**Base Model:** Mini-LLM (from-scratch decoder-only Transformer, GPT-style, RoPE-enabled)

**Training Dataset:** WikiText-2 + TinyStories + TechNews (domain-adaptive pretraining corpus)

**Implementation:** PyTorch (custom Transformer implementation with RoPE, AMP training, and gradient accumulation)

#### 4.1 Training Environment

- **Primary environment**: Local GPU workstation (NVIDIA CUDA-enabled GPU)
- **Framework**: PyTorch
- **Mixed precision**: Enabled via Automatic Mixed Precision (AMP)
- **Reproducibility**: Fixed random seed (seed = 42)
- **Training control**: YAML-based configuration (model.yaml, training.yaml)

The training loop supports CPU, CUDA, and MPS backends with automatic device selection.

#### 4.2 Dataset Preprocessing

Training data was constructed using a custom preprocessing pipeline:

**Dataset sources:**
- WikiText-2 (general encyclopedic text)
- TinyStories (simple narrative text for fluency)
- TechNews (technology-domain adaptation)

**Preprocessing steps:**
- Text cleaning (empty and malformed entries removed)
- Dataset-level deduplication (to prevent memorisation and leakage)
- Controlled dataset mixing (balanced general + tech domains)
- Train/validation/test split (90% / 5% / 5%)

**Output format:**
- JSONL files with explicit source tagging
- Converted to tokenized .pt files for efficient loading

This ensured a clean, reproducible, and leakage-free training corpus.

#### 4.3 Training Configuration

**Key hyperparameters** (from model.yaml and training.yaml):

**Model architecture:**
- Vocabulary size: 50,257
- Context length: 384 tokens
- Hidden size: 1024
- Layers: 24
- Attention heads: 16
- Feed-forward dimension: 4096
- Positional encoding: Rotary Positional Embeddings (RoPE)
- Weight tying: Enabled

**Training setup:**
- Epochs: 10
- Batch size: 12
- Gradient accumulation steps: 8 → Effective batch size = 96
- Optimizer: AdamW
- Learning rate: 3e-4 (cosine decay)
- Warmup steps: 500
- Gradient clipping: 1.0
- Dropout: 0.1

#### 4.4 Fine-Tuning / Training Approach

- The model was trained from scratch (no pretrained weights)
- **Objective**: Causal language modelling (next-token prediction)
- **Loss function**: Cross-entropy over shifted tokens
- Validation loss and perplexity evaluated periodically
- Best checkpoint selected based on lowest validation loss
- No instruction tuning or RLHF was applied; the model represents a base language model

#### 4.5 Model Saving and Loading

- Checkpoints saved every 500 steps
- Best-performing checkpoint tracked automatically
- **Saved artifacts include:**
  - Model weights
  - Optimizer state
  - Scheduler state
  - Training metadata

Model loading is handled via explicit checkpoint restoration for evaluation and inference.

#### 4.6 Performance Benchmarks

- **Final validation perplexity**: ~16
- **Generation quality**: Coherent long-form text with domain exposure
- **Technology-domain behaviour**: Improved technical vocabulary after TechNews integration

**Limitations observed:**
- No instruction-following guarantees
- No structured output (JSON) reliability without fine-tuning

These results are consistent with expectations for a medium-scale, from-scratch language model.

**Comments:**

The custom Mini-LLM demonstrates:
- Successful end-to-end training from scratch
- Stable convergence with modern optimisation techniques
- Domain-adaptive behaviour through curated data mixing
- Clear separation between base language modelling and instruction alignment

This model serves as the custom baseline for comparison against the zero-shot model in the frontend dashboard.

### V. Frontend Integration (Future Work)

#### 5.1 Backend API Integration

To connect live models to the frontend interface:

**1. Create backend evaluation endpoint:**
```
POST /api/v2/compare
Body: { "prompt": "user input text" }
Response: {
  "zeroShot": "model output",
  "custom": "model output"
}
```

**2. Update `app.js` comparison logic:**
- Replace `sampleResponses` lookup with fetch() call to backend
- Add loading states during API calls
- Handle API errors gracefully
- Stream responses if models support it for more realistic animation

**3. Backend implementation requirements:**
- Load both models on server startup
- Accept prompt via POST endpoint
- Run inference on both models
- Return JSON response with both outputs
- Add timeout handling (30-60 second limit)
- Log all requests for evaluation tracking

#### 5.2 Model Serving Options

**Option A: Direct Integration**
- Load models in backend server (Node.js/Python)
- Run inference synchronously per request
- **Pros**: Simple architecture, no additional services
- **Cons**: Memory intensive, limited concurrency

**Option B: Microservice Architecture**
- Deploy models as separate FastAPI services
- Backend proxies requests to model services
- **Pros**: Scalable, isolated model runtime
- **Cons**: Additional deployment complexity

**Option C: GPU Server Integration**
- Connect to existing university GPU infrastructure
- Backend makes HTTP calls to GPU server endpoints
- **Pros**: Leverage existing resources, faster inference
- **Cons**: Network latency, dependency on external service

#### 5.3 Integration Checklist

- [ ] Set up model serving infrastructure (GPU/CPU)
- [ ] Implement backend `/api/v2/compare` endpoint
- [ ] Update frontend to call live API instead of static responses
- [ ] Add error handling for model failures
- [ ] Implement request queuing if needed for concurrent users
- [ ] Add response caching for common prompts (optional)
- [ ] Test with HD panel demonstration requirements
- [ ] Document deployment procedures

## Next Steps

### 1. Complete model documentation (Section III & IV above)
- Document zero-shot model setup by Matt/Thai
- Document custom model training process by David/team

### 2. Backend integration preparation
- Review backend handover document structure
- Design API contract for comparison endpoint
- Plan model deployment strategy (Option A/B/C)

### 3. HD Panel Preparation
- Finalize 4 demonstration prompts
- Test animation timing for presentation flow
- Prepare talking points about dual-track architecture
- Create backup static demo in case of technical issues

### 4. Post-HD Panel
- Implement live backend integration
- Expand prompt library beyond 4 samples
- Add result export/download functionality
- Consider adding confidence scores or other metadata to outputs

## File Structure

```
dashboard/
├── index.html          # Landing page
├── metrics.html        # Evaluation metrics display
├── comparison.html     # Interactive comparison interface
├── app.js             # Application logic and data
└── styles.css         # Custom styling
```

## Usage Instructions

### Local Testing

1. Download all 5 files to the same directory
2. Open `comparison.html` in web browser
3. Type one of the 4 test prompts exactly
4. Click Submit or press Enter
5. Watch animated output appear in both boxes
6. Click "New Chat" to test another prompt

### Deployment

1. Copy files to web server directory
2. No build process required
3. Ensure all files maintain relative paths
4. Test all navigation links work correctly

## References

**Models:**
- Qwen 2.5-3B-Instruct (zero-shot)
- Custom Mini-LLM (SharePoint link at top of document)
