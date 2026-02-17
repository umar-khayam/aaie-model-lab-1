# **Environment Setup Guide – LLM Build Project**

Trimester 3, 2025.

Planner task: [Link to MS Planner](https://planner.cloud.microsoft/webui/v1/plan/uYcXdi9j10q2XjnDautR7MgAFL1s/view/board/task/rYAr0jAfNku_1dHYhnlBDsgALW5z?tid=d02378ec-1688-46d5-8540-1c28b5f470f6).  

**Project Leads:** Thai Ha NGUYEN, David Tenni, Matthew O’Donnell.  
**Document contribution:** Thai Ha NGUYEN.

This repository contains the environment configuration for the **AAIE LLM Build Pipeline**, supporting macOS, Windows, and Linux.

Two environment installation paths are provided:

* **Conda environment (recommended)** → `environment.yml`
* **pip virtual environment** → `requirements.txt`

## 1. System Requirements

Before setting up the environment:

### **Required**

* Python **3.10**
* Git
* Stable network connection

### **Optional (recommended)**

* Conda / Miniconda
* GPU drivers

  * **CUDA** for Nvidia GPUs (Windows/Linux)
  * **Metal (MPS)** for macOS Silicon


## 2. Install Environment (Conda – Recommended)

### **Create the environment**

```bash
conda env create -f environment.yml
```

### **Activate**

```bash
conda activate llm-build
```

### **Update later**

```bash
conda env update -f environment.yml --prune
```

## 3. Install Environment Using pip (Alternative)

### **Create venv**

macOS / Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows:

```powershell
python -m venv .venv
.\.venv\Scripts\activate
```

### **Install dependencies**

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## 4. GPU Backend Notes (Important)

### **macOS Apple Silicon (M1/M2/M3)**

PyTorch automatically enables **MPS** (Metal Performance Shaders).

Check availability:

```bash
python - <<EOF
import torch
print(torch.backends.mps.is_available())
EOF
```

### **Windows + Linux (Nvidia CUDA)**

Install CUDA-enabled PyTorch if you want GPU acceleration:

Example CUDA 12.1:

```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

Check CUDA:

```bash
python - <<EOF
import torch
print(torch.cuda.is_available())
print(torch.cuda.get_device_name(0) if torch.cuda.is_available() else "No GPU")
EOF
```

### **BitsAndBytes Notes**

* Linux: full GPU support
* Windows: CPU-only mode
* macOS: not supported

This does **not** break training; QLoRA simply falls back gracefully.

## 5. Test Your Environment

Run:

```bash
python device_test.py
```

(or copy this snippet)

```python
import torch
print("Torch:", torch.__version__)
print("CUDA:", torch.cuda.is_available())
print("MPS :", torch.backends.mps.is_available() if hasattr(torch.backends, 'mps') else False)

x = torch.rand(2,2)
print("Tensor OK:", x)
```

## 6. Project Structure (Recommended)

```
aaie-llm-mini/environments/
├── environment.yml
├── requirements.txt
├── README.md

```


## Troubleshooting

### 1. MPS error on macOS:

Update PyTorch:

```bash
pip install --upgrade torch torchvision torchaudio
```

### 2. CUDA not found:

Install correct Nvidia driver + CUDA build.

### 3. BitsAndBytes load fail:

Expected on Windows/macOS → safe to ignore.