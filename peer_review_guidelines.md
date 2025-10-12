# Peer Review Guidelines (Model Development Team)

Welcome! This document explains how to review a pull request (PR) in GitHub for the Model Development Team. Reviewing ensures our codebase, experiments, and documentation remain consistent, reproducible, and high quality.


## Quick-Start Review Checklist
Use this checklist for every PR:

- **Read PR Description**
  - Clear explanation of changes?
  - Purpose and scope understandable?

- **Check Files Changed**
  - Code style consistent and readable?
  - Functions/classes documented?
  - No hardcoded paths, secrets, or junk files?
  - Documentation/reports consistent in style and naming?

- **Validate Experiments**
  - Results/metrics (accuracy, latency, cost) explained?
  - Scripts/configs reproducible?

- **Decide Review Outcome**
  - Approve – Ready to merge
  - Comment – Feedback, but not blocking
  - Request changes – Must fix before merge


## Detailed Reviewer Guide

### 1. When Do I Review a PR?
When someone creates a PR to add or update code, experiments, or documentation, they will request at least two peer reviewers and one  lead reviewer.

Check:
- Is the PR description clear and complete?
- Is the code structured, readable, and following conventions?
- Are experiments reproducible (scripts, configs, datasets linked)?
- Are results and evaluation metrics documented?
- Does the change improve reliability without breaking existing workflows?


### 2. How to Find a PR
PRs are **not directly assigned** to you. Instead:

1. Check the **team announcements** channel for new PR notifications.  
2. Look for PRs in topics you are familiar with (e.g., models, prompts, evaluation scripts, docs).  
3. Follow the link in the announcement to open the PR.  
4. Start reviewing by reading the description and checking the files.  

**Note:** Each member is expected to complete **at least 5 peer reviews** to be eligible to pass. Peer review is considered an important contribution to the project.


### 3. Read the PR Description
At the top of the PR, you’ll see a title and description explaining what the contributor changed.  
Read this carefully to understand what the PR is about (e.g., new model component, bug fix, evaluation update).


### 4. Review the Files
1. Click the **Files changed** tab  
2. Read through the modified code and documentation  
3. Check for:
   - Correct coding style and readability  
   - Proper function and class documentation  
   - Tests included or updated  
   - Experiment configs and outputs clearly referenced  
   - No hardcoded paths, secrets, or unnecessary files committed  

Tip: Leave line-by-line comments by clicking the **+** next to a line.


### 5. Approve or Request Changes

#### Public Repos
- Reviewers can use GitHub’s built-in **Approve**, **Comment**, or **Request changes** buttons.  
- A PR should ideally have **≥2 approvals + 1 senior lead** before merge.  

#### Private Repos (Free Plan / No Branch Protections)
- Formal “Approve/Request changes” may not be available.  
- In this case, reviewers **leave comments** with clear intent:
  - *Looks good, approved*  
  - *Comment only – suggestion for improvement*  
  - *Requesting changes – must fix before merge*  
- The **lead reviewer/admin** merges once there is enough consensus in comments.  


## Thank You
By following this guide, you help us maintain a robust, reproducible, and high-quality model development workflow. Whether the repo is public or private, the principles remain the same: **clarity, reproducibility, security, and constructive feedback.**

##### Credits: Qasim Nasir, Arnav Ahuja
