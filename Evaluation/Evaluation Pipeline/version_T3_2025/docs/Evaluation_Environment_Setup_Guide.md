# Evaluation Environment Setup Guide with Python

Trimester: Trimester 3, 2025  
Student: Matthew O’Donnell

This notebook details how to set up a new python environment for running the Evaluation pipeline that tests LLMs performance which is reproducible across MacOS, Windows, & Linux systems.

It covers:

1. System prerequisites (Conda / Homebrew)  
2. Environmental creation (Isolation)  
3. Dependency management (`pip` and `requirements.txt`)  
4. Hardware acceleration setup (`cuda`, `mps`, & `cpu`)

## **Phase 1: System Prerequisites**

Before creating python environments, we will need a package manager. For this we have used **Miniforge** (a minimal installer for Conda) because it defaults to the community-driven `conda-forge` channel and avoids licensing issues associated with Anaconda.

### **MacOS Setup**

**1\. Install Homebrew (if not installed):** Open your terminal and run:

    `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`

*For more information on homebrew, please visit [https://brew.sh/](https://brew.sh/).*

**2\. Install Miniforge:**

    `brew install miniforge`  
    `conda init zsh  # Restart terminal after this`

*For more information on MiniForge, please visit [https://github.com/conda-forge/miniforge](https://github.com/conda-forge/miniforge).*

### **Windows Setup**

**1\. Download Installer:** Download the Miniforge3-Windows-x86\_64.exe from the [Miniforge GitHub](https://github.com/conda-forge/miniforge).

**2\. Install:** Run the `.exe`. Check the box that says **"Add Miniforge3 to my PATH environment variable"** (or use the Anaconda Prompt terminal provided).

### **Linux Setup**

**1\. Download and Run Script:**

    `curl -L -O "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh"`  
    `bash Miniforge3-Linux-x86_64.sh`

## **Phase 2: Creating the Virtual Environment**

To create a virtual environment (very important to not corrupt our base system environment) we will use Conda to create an isolated "box" for this project. This prevents conflicts with other projects, as well as the base system.

### Create a virtual environment

Replace `my_env_name` with your desired project name.

    `conda create --name my_env_name`

### Activate virtual environment

note that you must do this every time you work on the project.

    `conda activate my_env_name`

*For more information about creating virtual environments, please visit [https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html\#creating-an-environment-with-commands](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#creating-an-environment-with-commands).*

## **Phase 3: Dependency Management (Pip & Requirements)**

While Conda is great for creating the environment, we will use `pip` as it is often better for installing specific Python libraries.

### Install pip and / or update if needed:

`conda install pip -y`

`python -m pip install --upgrade pip`

*For more information on installing or using pip, please visit [https://pypi.org/project/pip/](https://pypi.org/project/pip/).*

### Install `requirements.txt` file

The requirements file are found within the evaluation/testing/eval\_pipeline\_version\_1  
`pip install -r requirements.txt`

To verify that the libraries are correctly installed, place the following in the terminal while still in your virtual environment.

`pip freeze`

*Please note that for MacOS, sometimes the llama_cpp_python fails, if so, please ensure that you have agreed to xcodes licence (run `sudo xcodebuild -license`) and agree, then try to install requirements.txt again. If this still fails, run: `CMAKE_ARGS="-DGGML_METAL=on" pip install llama-cpp-python --upgrade --force-reinstall --no-cache-dir`.*

## **Phase 4: Verification**

Once you have installed the libraries using the commands above, run the following cell to verify that your environment is utilizing your hardware correctly.

`import torch`  
`import sys`

`print(f"🐍 Python Version: {sys.version.split()[0]}")`  
`print(f"🔥 PyTorch Version: {torch.__version__}")`  
`print("-" * 30)`

`if torch.cuda.is_available():`  
    `print("✅ Hardware Acceleration: CUDA (NVIDIA) is ACTIVE")`  
    `print(f"   Device Name: {torch.cuda.get_device_name(0)}")`  
    `device = "cuda"`  
`elif torch.backends.mps.is_available():`  
    `print("✅ Hardware Acceleration: MPS (Apple Silicon) is ACTIVE")`  
    `device = "mps"`  
`else:`  
    `print("⚠️ Hardware Acceleration: None (Running on CPU)")`  
    `device = "cpu"`

`print(f"   Active Device String: '{device}'")`

`# Simple Tensor Test`  
`x = torch.rand(5, 3).to(device)`  
`print("\nTest Tensor successfully created on device:")`  
`print(x)`

You should now have the correct environment setup and be able to run the `evaluation_pipeline_v1.ipynb`.