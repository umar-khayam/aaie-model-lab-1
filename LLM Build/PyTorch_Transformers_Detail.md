# LLM Development Framework Selection: Pytorch and Transformers
**Author:** ***Matthew O’Donnell***

**Aim:** Selecting an appropriate framework for building a “from scratch” LLM with exceptional cross-platform compatibility.

The pipeline will be architected exclusively on the PyTorch deep learning framework, along with transformers for model development. This decision is driven by the requirement for a hardware-agnostic foundation that supports a "from scratch" architectural development approach while maintaining seamless interoperability between heterogeneous development environments and deployment infrastructure (Apple Silicone with MacOS, Nvidia with Cuda, AMD with ROCm, and Google with their TPU’s).

**Core Architecture: PyTorch + Hugging Face Transformers**  
The development pipeline will be architected exclusively on PyTorch which will be utilised in conjunction with the Hugging Face Transformers library. This decision is driven by the strict requirement for a hardware-agnostic foundation that supports granular architectural control while maintaining seamless team interoperability.  
***Why not TensorFlow…*** We have explicitly excluded TensorFlow/Keras to avoid the ‘two-stack reality’. As noted in recent market analysis, over 80% of modern LLM research is published natively in PyTorch [1]. Adopting TensorFlow would impose a ‘Translation Tax’ here, that is the requirement to manually port mathematical concepts and reference implementations from PyTorch to Keras, introducing latency and parity errors, thus detracting from computational efficiency.

**Cross-Platform Hardware Abstraction**  
The primary logistical constraint is the team's heterogeneous infrastructure. We will utilise Hugging Face Accelerate as the orchestration layer to abstract these differences [2], thus enabling a single codebase to run dynamically on the following systems:  
- ***MacOS (Apple Silicon)***  
    Leveraging the MPS (Metal Performance Shaders) backend [3], allowing local model logic to function identically to server-side code without separate codebases.     
- ***Nvidia and AMD (Windows/ Linux)***   
    Native CUDA optimisation for high-throughput training. Note that ROCm by AMD can also now be utilized [4], however, you will need to install dependencies and use Docker. For further information, please see the following documentation from the AMD dev team: https://rocm.docs.amd.com/projects/install-on-linux/en/latest/install/3rd-party/pytorch-install.html   
- ***Google TPU***  
Unlike standard PyTorch device calls, our pipeline will support XLA (Accelerated Linear Algebra) integration for TPUs via the unified Accelerator interface, ensuring Google Colab compatibility without refactoring the training loop.

**Architectural Control vs. Abstraction**  
Developing a LLM build pipeline from scratch requires granular control over the training loop and model architecture, which high-level abstractions like Keras 3 often obscure.

**Eager Execution & Debugging**  
PyTorch’s “define-by-run" philosophy allows for standard Python debugging (using pdb or print statements) of complex logic such as dynamic routing or conditional masking. This contrasts with the static graph generation of Keras where error messages can be relatively opaque and disconnected from the Python source.

**Performance via Compilation**  
While offering the flexibility of Python during development, PyTorch 2.0 bridges the performance gap via torch.compile and TorchInductor [5]. This allows the project to maintain a readable Python codebase that is compiled into optimised kernels (using OpenAI Triton) for production, thus ensuring research agility does not come at the cost of throughput.

**Minimising the ‘Translation Tax’ of Research**  
Recent market analysis indicates that over 80% of modern AI research and Large Language Model (LLM) architectures are published first in PyTorch [1]. Adopting alternative frameworks (like JAX or Keras etc) would impose a ‘translation tax’ which would result in requiring the manual porting of mathematical concepts and reference implementations, which introduces latency and potential parity errors. By standardising on PyTorch, the project aligns with the dominant research ecosystem, granting immediate access to state of the art techniques such as FlashAttention [6] and FSDP (Fully Sharded Data Parallel) [7] without integration delays.

## Setting up PyTorch and Transformers

The following code is required to run the PyTorch and Transformer libraries. It is important to ensure the correct packages are installed on the corresponding frameworks.

**PyTorch installation**

For ***MacOS*** with ***Apple Silicone*** (M1, M2, M3, M4, & M5):

```
pip install torch torchvision
```

For ***Windows/Linux*** with ***Nvidia GPU*** (CUDA):
Note you need to specify version with CUDA support

```
# Note this is the standard command for CUDA 11.8 (common stable version) 
pip install torch --index-url https://download.pytorch.org/whl/cu118
```

For ***CPU only*** (no GPU):
If you are running on CPU only, this will be very slow compared to a GPU.

```
pip install torch
```

**Transformers installation**  
The following installs the HuggingFace transformers library.

```
pip install transformers
```

### **Automated Device selection code**  
The following code is designed to act as a universal device selection, and checks to see if PyTorch and Transformers are installed. Furthering this, it prints the respective Python version, PyTorch version, and Transformers version used within the environment. Please ensure that you are using the verions outlined in the requirements documentaiton.

Code File -> *pytorch_device_selection.py*

```
"""Utility to select the best compute device and print environment info.
Supports TPU, CUDA (Nvidia/AMD), MPS (Apple Silicon), and CPU."""

import torch
import sys
import logging

# Start with the config of logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_compute_device():
    """
    Here it selects the best available compute device for the current environment.
    This supports the following accelerators:
    1. Google TPU (via torch_xla)
    2. Nvidia GPU (CUDA)
    3. Apple Silicon (MPS)
    4. AMD GPU (ROCm - maps to CUDA usually)
    5. CPU (Fallback)
    """
    
    # 1. Check for TPU (Google Colab / Cloud TPU)
    # TPUs require the torch_xla library, so we check for this here.
    try:
        import torch_xla.core.xla_model as xm
        device = xm.xla_device()
        logger.info(f"Acceleration: Google TPU detected via torch_xla. Device: {device}")
        return device
    except ImportError:
        pass # not a TPU environment

    # 2. Check for CUDA (Nvidia or AMD ROCm via CUDA-compatibility so will appear as Cuda)
    if torch.cuda.is_available():
        device = torch.device("cuda")
        device_name = torch.cuda.get_device_name(0)
        logger.info(f"Acceleration: CUDA detected. GPU: {device_name}")
        return device

    # 3. Check for MPS (Apple Silicon M-Series chips)
    if torch.backends.mps.is_available():
        if torch.backends.mps.is_built():
            device = torch.device("mps")
            logger.info("Acceleration: Apple Silicon (MPS) detected.")
            return device
        else:
            logger.warning("MPS is available but not built. Falling back...")

    # 4. Fallback to CPU if none else is available
    logger.warning("No hardware acceleration detected. Using CPU (computationally slow).")
    return torch.device("cpu")

def print_environment_info():
    """
    Prints version info for debugging purposes.
    """
    print(f"Python Version: {sys.version.split()[0]}")
    print(f"PyTorch Version: {torch.__version__}")
    
    # Check for Hugging Face Transformers
    try:
        import transformers
        print(f"Transformers Version: {transformers.__version__}")
    except ImportError:
        print("Transformers Version: Not Installed. Please install via 'pip install transformers'")

if __name__ == "__main__":
    print("=== Environment Setup Check ===")
    print_environment_info()
    device = get_compute_device()
    
    #Example Tensor test
    x = torch.rand(3, 3).to(device)
    y = torch.rand(3, 3).to(device)
    z = x + y
    print(f"\nTensor Operation Test on {device}: Success")
    print(z)
```

**References**  
[1] Z. B. Alawi, (2025). A Comparative Survey of PyTorch vs TensorFlow for Deep Learning: Usability, Performance, and Deployment Trade-offs,. arXiv preprint arXiv:2508.04035. Available: https://arxiv.org/html/2508.04035v1

[2] Gugger, S., et al. (2022). Accelerate: Training and inference at scale made simple. GitHub Repository. Available: https://github.com/huggingface/accelerate

[3] Apple Inc. (2024). Accelerated PyTorch training on Mac. Metal Developer Documentation. Available: https://developer.apple.com/metal/pytorch/

[4] Advanced Micro Devices, Inc (AMD). (2024). ROCm Support for PyTorch. AMD Infinity Hub. Available: https://rocm.docs.amd.com/en/latest/

[5] Ansel, J., et al. (2024). PyTorch 2: Faster Machine Learning through Dynamic Python Bytecode Transformation and Graph Compilation. ACM International Conference on Architectural Support for Programming Languages and Operating Systems (ASPLOS).

[6] Dao, T., Fu, D. Y., Ermon, S., Rudra, A., & Ré, C. (2022). FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness. Advances in Neural Information Processing Systems (NeurIPS).

[7] Zhao, Y., Gu, A., Varma, R., Luo, L., Huang, C.-C., Xu, M., Wright, L., et al. (2023). PyTorch FSDP: Experiences on Scaling Distributed Training. Proceedings of the VLDB Endowment.

[8] Wolf, T., et al. (2020). Transformers: State-of-the-Art Natural Language Processing. Proceedings of the 2020 Conference on Empirical Methods in Natural Language Processing: System Demonstrations.