# Complete Local Training Run

*Trimester 3, 2025*

Planner task: [Link to MS Planner](https://planner.cloud.microsoft/webui/v1/plan/uYcXdi9j10q2XjnDautR7MgAFL1s/view/board/task/tKrIXnfVbEqA_RaO1d8x88gABkQG?tid=d02378ec-1688-46d5-8540-1c28b5f470f6).  

**Project Leads:** Thai Ha NGUYEN, David Tenni, Matthew O’Donnell.  
**Document contribution:** Thai Ha NGUYEN.

## Objective

Execute a full end-to-end **local training run** for the Mini-LLaMA model, including data preprocessing, dataset construction, multi-epoch training, checkpointing, and final evaluation, to validate training stability and baseline model quality.

# Complete trained Mini-LLM model

- Download: [Mini-LLM-AAIE](https://deakin365.sharepoint.com/:u:/r/sites/Deakin-MITHackathon/Shared%20Documents/AAIE%20-%20Artificial%20Assessment%20Intelligence%20for%20Educ/Mini-LLM%20model/Pytorch%20Model/step_6000.pt?csf=1&web=1&e=uS8hGi)

## Hardware & Environment

* **GPU**: NVIDIA A40
* **VRAM**: 48GB GDDR6
* **Compute Backend**: CUDA
* **Execution Environment**: Docker / CUDA-enabled Python environment (`cudaenv`)
* **Training Mode**: Single-GPU, full-parameter training

This setup was sufficient to support multi-epoch training without out-of-memory errors or gradient instability.

## Dataset Preparation

### Source Dataset

* Additional Domain dataset: **Cosmopedia/OpenStax** (educational textbook corpus)

### Dataset Statistics

* Total documents: **126,332**
* Duplicate documents removed: **0**

### Dataset Split

| Split      | Documents |
| ---------- | --------- |
| Train      | 113,698   |
| Validation | 6,316     |
| Test       | 6,318     |

### Outputs

* `train.pt`
* `val.pt`
* `test.pt`

All datasets were successfully preprocessed and serialized for training.


## Training Configuration (Summary)

* **Total Epochs**: 5
* **Final Training Step**: 6,050
* **Checkpointing**: Periodic (every ~500 steps)
* **Evaluation**: Validation loss and perplexity computed regularly during training

Training ran continuously across all epochs without interruption.


## Training Progress Overview

### Convergence Behavior

* Initial training loss decreased rapidly from **~7.3** to **<3.0** within the first epoch.
* Steady and consistent improvement observed across all epochs.
* No signs of divergence, exploding gradients, or overfitting.

### Validation Performance Trend

| Epoch   | Val Loss | Val Perplexity |
| ------- | -------- | -------------- |
| Epoch 1 | 3.11     | 22.46          |
| Epoch 2 | 2.64     | 14.02          |
| Epoch 3 | 2.40     | 11.05          |
| Epoch 4 | 2.33     | 10.30          |
| Epoch 5 | 2.27     | 9.68           |

Validation perplexity decreased smoothly, indicating effective generalization.


## Checkpoints Generated

Key checkpoints saved during training:

* `step_500.pt`
* `...`
* `step_6000.pt` (final)


## Final Evaluation Results

Evaluation performed using the final checkpoint (`step_6000.pt`) on the held-out test set.

### Test Metrics

* **Test Loss**: **2.2626**
* **Test Perplexity**: **9.61**

These results indicate strong baseline language modeling performance for a locally trained Mini-LLaMA-scale model.

---

## Outcome & Acceptance Criteria

* Full local training pipeline executed successfully
* Model converged smoothly across all epochs
* Validation and test perplexity reached stable low values
* Final checkpoint produced and evaluated
* No hardware, memory, or runtime failures

## Notes & Next Steps

* Model is ready for:

  * Fine-tuning (instruction, domain-specific, or PEFT/LoRA)
  * Conversion to inference-optimized formats (e.g. GGUF for LM Studio / Ollama)
  * Downstream evaluation tasks (generation quality, benchmarks)

* Future work may explore:

  * Longer training schedules
  * Learning rate decay strategies
  * Scaling dataset diversity beyond OpenStax
