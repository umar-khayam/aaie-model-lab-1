# **LLM Prompting Experimentation Plan**  
*Objective: Test and optimise prompts for generating student assessments and detecting AI generated content, utilising commercial and open-source LLMs.*  

---

## **1. Process & Workflow**  
### **High-Level Steps**  
1. **Define Scope**  
   - **Task:** Rubric-based assessment generation and AI content detection  
   - **LLMs:** GPT-4, Gemini, Qwen, TinyLlama, Mistral, Gemma, Phi  
   - **Variables:** Prompt design (few-shot/zero-shot), temperature, output length

2. **Pipeline Design**  
   ```mermaid
   graph LR
   A[Prompt Templates] --> B[LLM APIs/Local Models]
   B --> C[Response Collection]
   C --> D[Evaluation: Human + Auto]
   D --> E[Gap Analysis]
   E --> F[Iterate on Prompts]
   ```

3. **Automation**  
   - Commence initial automated pipeline experimentation in python notebooks eg: Colab/Jupyter
   - Move to python .py files 
   - Merge to single script to parallelise API calls and inference (python + `asyncio`/`multiprocessing`)
   - Analyse, review, implement frameworks for integration e.g., Langchain, Huggingface, etc
   - Investigate deployments options - container, GitHub Actions/CI-CD,  cloud options e.g., AWS SageMaker, GCP Vertex, other

### **Key Principles**  
- **Outcome-Driven:** Focus on actionable insights 
- **Automation-First:** Minimize manual steps in testing/evaluation
- **Documentation-as-Code:**  
  - Version prompts, scripts, and results in Git.  
  - Provide useful git commit message
  - Use `.md` files if required for additional documentation. Avoid .doc , .pdf


---

## **2. Path Forward**  
### **Phase 1: Baseline Setup**  
- **Deliverables:**  
  - Implement and parse json files from Data team as baseline constant 
  - Standardised prompt templates - research prompt library for version control
  - API access/local model setup  

### **Phase 2: Initial Testing**  
- **Tasks:**  
  - Run baseline prompts across all LLMs.  
  - Log outputs with metadata (model, latency, token count) 
  - Example: Refer AAIE_Prompting_Design_Qwen.ipynb

### **Phase 3: Evaluation & Gaps**  
- **Metrics:**  
  - Team to finalise metrics and evaluation process  
  - **Gap Identification:**  
    - Common failure modes (e.g., hallucinations)
    - Model-specific weaknesses (e.g., Gemini over-explains, TinyLlama lacks depth)  

### **Phase 4: Iteration**  
- **Improvements:**  
  - Refine prompts (add examples, clarify constraints)
  - Test advanced techniques (chain-of-thought, self-correction)  

---

## **3. Technical Guidance for Team**  
### **Tools & Infrastructure**  
- **APIs:** Azure, Google, Huggingface Inference
- **Local Models:** Huggingface , Ollama + vLLM for open-source
- **Storage:** JSON logs (AWS S3/SQLite).  
- **Evaluation:**  
  - Human: Rubric scoring (1–5 scale)
  - Auto: ROUGE, BERTScore, etc  
- **Deployment:** AWS, GCP, other

---

## **4. Deliverables (Product Artifacts)**  
1. **Documentation:**  
   - **Experiment Report** (MD): Methodology, results, gaps
   - **Prompt Catalog** (JSON/CSV): Optimised prompts per model 
2. **Pipeline Code** (Git Repo):  
   - Scripts for API calls, evaluation  
3. **Dashboard** (Optional):  
   - Visualise performance metrics (accuracy, latency)

---

### **Next Steps**  
1. Assign roles   
2. Kick off Phase 1 
3. Schedule weekly syncs to review progress and gaps  
