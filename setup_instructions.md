# Setup Instructions

Welcome! If you're contributing to the aaie-model-lab repo for the first time, follow these steps to set up your local environment and start your work. This guide assumes **no prior experience with GitHub**, so everything is explained step by step.


## 1. Fork the Repository

To contribute, you first need your own copy of the project.

1. Go to the original GitHub repository:  
   [https://github.com/InnovAIte-Deakin/aaie-model-lab](https://github.com/InnovAIte-Deakin/aaie-data-hub)

2. Click the **“Fork”** button in the top-right corner.

3. **IMPORTANT**: Make sure you **fork the entire repository**, not just the `main` branch. Keep all branches including `development`.


## 2. Clone Your Forked Repository

Now, copy the project to your computer.

1. Open your forked repository on GitHub (under your username).
2. Click the green **"Code"** button and copy the HTTPS link.
3. Open a terminal (e.g., Git Bash or VS Code terminal), then run:

```bash
git clone https://github.com/your-username/aaie-model-lab.git
cd aaie-model-lab
```


## 3. Connect to the Original Repository (Upstream)

This lets you get updates from the main project.

```bash
git remote add upstream https://github.com/InnovAIte-Deakin/aaie-model-lab.git
```


## 4. Create a Branch Based on `development`

You must always base your changes on the **latest `development` branch**.

```bash
git fetch upstream
git checkout -b your-branch-name upstream/development
```

Replace `your-branch-name` with something short and descriptive (e.g., `add-contributor-guide`).


## 5. Make Your Changes

Edit, add, or create files as required for your task.

Make sure everything follows the format and folder structure set by the project:

- **`/API Integration/`** → API-related documentation, scripts, and integration code  
- **`/Deprecated/`** → Old or replaced code, experiments, or notes (kept only for archival purposes)  
- **`/Evaluation/`** → Scripts, notebooks, and reports on AI detection and feedback evaluation/benchmarking  
- **`/Experimental Plan/`** → Proposals, design docs, and experiment planning documents  
- **`/Fine Tuning Research/`** → Notes, scripts, and results related to fine-tuning research and studies  
- **`/Infrastructure and Development/`** → Infrastructure setup, DevOps, and environment-related docs or code  
- **`/Model and Prompt Selection/`** → Base prompts, datasets, and model evaluation reports for Phase 1 and beyond  
- **`/Upskilling Docs/`** → Learning resources, tutorials, training materials, and peer review guidelines  


## 6. Commit and Push to Your Fork (Origin)

After making your changes:

```bash
git add .
git commit -m "Your clear and concise commit message"
git push origin your-branch-name
```


## 7. Create a Pull Request (PR)

1. Go to your forked repository on GitHub.
2. You’ll see a **“Compare & pull request”** button — click it.
3. Make sure:
   - **Base repo** = `InnovAIte-Deakin/aaie-model-lab`
   - **Base branch** = `development`
   - **Head repo** = your fork
   - **Compare branch** = the one you pushed

4. Add a short title and description, then click **Create Pull Request**.


## 8. Request Reviews and Follow Up

Once your PR is created:

1. **Post the PR link** in the Teams channel and tag the people who agreed to review your work.
2. **Assign the reviewers** to the corresponding task card in MS Planner.
3. If your PR is not reviewed within **2 days**, follow up with a reminder.
4. If someone cannot review after being assigned, **find a replacement reviewer** to keep things moving.
5. For full approval, you need:
   - 2 peer reviewers
   - 1 senior lead reviewer
   - Final review and merge by Mentor

Refer to [`PR review guidelines.md`](/reviewer_guide.md) for reviewer steps.


You're done!  

**NOTE**: If you need to make changes after submitting your PR, just commit and push to the same branch. The PR will automatically update. But if you want to work on a different task, create a **NEW** branch from `development` and repeat the process.

##### Credits: Qasim Nasir, Arnav Ahuja