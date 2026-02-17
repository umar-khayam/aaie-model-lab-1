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

    # 4. Fallback to CPU is none else is available
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