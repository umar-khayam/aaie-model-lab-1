# GPU Resource Request Justification
## AAIE Project - Custom LLM Development

**Date:** January 25, 2026  
**Prepared by:** David - LLM Fine-Tuning/Development Stream Lead  
**Project:** AAIE Capstone - Custom Mini-LLM for Educational Assessment

---

## Executive Summary

Our training progression demonstrates a direct, measurable correlation between GPU resources and model quality. We have clear evidence across three training stages showing that each order-of-magnitude increase in compute produces qualitatively better outputs. To deliver a production-ready educational assessment system for next trimester's doubled student load, we require **10-100x our current GPU capacity**.

---

## Training Progression: Evidence-Based Improvement

### Stage 1: Minimal Training (Few Million Tokens)
**Resources:** Limited dataset, minimal compute  
**Duration:** Initial proof-of-concept  
**Output Quality:** Completely unusable

#### Example Output:
**Prompt:** "Once upon a time, a small robot decided to"

**Model Output:**
```
toooooooooooooooooooooooooooooooooooooooooooooooo
```

**Analysis:** Model produced only repeated characters. No language understanding, no sentence structure, no coherence. This represents the absolute baseline - the model knows how to generate tokens but has learned no meaningful patterns.

---

### Stage 2: Initial Proper Training 
**Resources:** NVIDIA A40 48GB VRAM × 29 hours = 1,392 GPU-hours  
**Dataset:** DREsS dataset (properly tokenized)  
**Output Quality:** Coherent but off-topic, child-like narratives

#### Quantitative Metrics:
- Content Pearson: 0.084 (extremely weak correlation)
- Organization Pearson: 0.185 (weak correlation)
- Language Pearson: 0.239 (poor correlation)
- Overall Kappa: 0.216 (poor agreement)
- Judge Metrics: Averaging 0.5-0.6 (barely better than random)

#### Example Outputs:

**Prompt 1:** "Once upon a time, a small robot decided to"

**Model Output:**
```
Once upon a time, a small robot decided to reverse. He ran and ran until he 
reached a big tree. Then he jumped and went to the tree. He looked high and 
low and saw a beautiful rainbow in the sky. The robot was very happy.

He started to climb the tree and try to find a place to hide. He looked around 
and he saw a big tree. He climbed and climbed until he finally made it to the 
top. It was a beautiful park with many trees and a pond.

The robot was so
```

**Analysis:** Grammatically coherent sentences with proper structure. However, the narrative wanders aimlessly between actions with no clear purpose or educational relevance. The robot "decides to reverse" then suddenly sees a rainbow - no logical progression.

---

**Prompt 2:** "Artificial intelligence will change education by"

**Model Output:**
```
Artificial intelligence will change education by a single tool on the grid, 
the report says. Once upon a time, there was a little girl named Lily. She 
loved to play with her toys, but sometimes she got dizzy. Her mommy told her 
to take a nap, but Lily didn't want to take a nap.

One day, Lily's mommy was washing her hair with soap and water. Lily didn't 
want to get sick, so she decided to take her to the store to buy a new sweater.
```

**Analysis:** Starts with a fragment that could be relevant ("by a single tool on the grid") but immediately derails into a completely unrelated children's story about Lily getting dizzy and buying a sweater. This demonstrates the model has learned narrative structure but not topic coherence or domain relevance.

---

**Prompt 3:** "Explain reinforcement learning in a simple way."

**Model Output:**
```
Explain reinforcement learning in a simple way. The stock price of Tesla Inc 
(NASDAQ: TSLA) increased by over 12% pre-market. This is why it happened. 
Once upon a time, there was a little girl named Lily. She loved to play with 
her toys, especially her dolls. One day, Lily's mom said, "Lily, we are going 
to deliver a new toy to your grandma. It's very expensive." Lily was so happy 
and said, "Yes, please!"

They got in
```

**Analysis:** Repeats the prompt verbatim, inserts random financial news about Tesla stock, then defaults to another "Lily" children's story. The model recognizes these are all "text patterns" but cannot distinguish between technical explanations, news, and narratives.

---

**Comparison to Zero-Shot Model (Same Prompt):**
```
Reinforcement Learning (RL) is a type of machine learning where an agent learns 
to make decisions by taking actions in an environment to achieve a goal. 

1. Agent: This is the entity that takes actions
2. Environment: The world or scenario in which the agent operates
3. Reward: The agent receives rewards or penalties for its actions
4. Learning Goal: Maximize cumulative reward over time

Example: Imagine playing a video game where your goal is to get the highest 
score possible. Each time you move your character, you receive a reward based 
on whether you hit enemies, collect coins, or avoid traps...
```

**Gap Analysis:** The zero-shot model provides structured, relevant, educational content. Our custom model at Stage 2 produces irrelevant narratives. This gap demonstrates insufficient training to learn domain-specific patterns.

---

### Stage 3: Current Training Results (Latest)
**Resources:** Extended training beyond initial 29 hours  
**Output Quality:** Improved context awareness, still requires refinement

#### Example Outputs:

**Prompt:** "Artificial intelligence is transforming the way"

**Model Output:**
```
Artificial intelligence is transforming the way humans work, especially in 
areas like computer science, engineering, and even social sciences! By 
harnessing the power of AI, scientists can gain access to vast opportunities 
for learning and growth. For example, you might be able to design a mobile 
app that allows users to access and manage files, making it easier to navigate 
and collaborate with colleagues. Or if you're running a small business, how 
does the software make you feel connected to other people's work?

But AI isn't just about finding the perfect fit. It's also about learning how 
to interpret and improve its own systems. When we
```

**Analysis:** Significantly improved! The model now:
- Stays on topic (AI and work/technology)
- Provides relevant examples (mobile apps, file management)
- Maintains coherent flow between ideas
- Shows domain awareness (computer science, engineering)

However, still shows some issues:
- "How does the software make you feel connected" - awkward phrasing
- Cuts off mid-thought ("When we")
- Could be more structured and academic in tone

---

**Prompt:** "In recent years, large language models have"

**Model Output:**
```
In recent years, large language models have gained significant traction within 
anthropological circles, often referred to as "sociologos" due to their 
reliance on visual cues and semantic meaning. However, these methods often 
fall short in capturing the nuances of social reality, leading to 
oversimplification and overlooks important contextual factors influencing 
communication (Kohn & Shammas, 2007; Hill, 2000). Consequently, we propose 
an alternative conceptualization of social reality that acknowledges both the 
affordances and limitations of such analytical tools.

Defining Social Context:
Social context refers to the broader sociohistorical context within which 
social phenomena are situated. It
```

**Analysis:** Major improvement in academic writing capability:
- Uses discipline-specific terminology
- Includes citations (though possibly hallucinated)
- Structured argument flow
- Appropriate academic tone

Still needs work:
- "Sociologos" is likely not a real term
- Citations may not be accurate
- Needs better grounding in factual information

---

## Clear Pattern: More Training = Better Quality

| Training Stage | GPU-Hours | Output Characteristics | Example |
|----------------|-----------|------------------------|---------|
| **Stage 1** | <100 | Only repeated characters | "toooooooo..." |
| **Stage 2** | 1,392 | Coherent but off-topic stories | "Lily got dizzy and bought a sweater" |
| **Stage 3** | ~5,000+ (estimated) | On-topic with context awareness | Relevant AI/tech discussions |
| **Target** | 13,920-139,200 | Production-ready assessment | Rubric-aligned evaluation |

---

## Resource Scaling Analysis

### Current Baseline
- **Hardware:** NVIDIA A40 48GB VRAM
- **Duration:** 29 hours
- **Total:** 1,392 GPU-hours

### Proposed Scaling Targets

#### Conservative (10x): Minimum Production Quality
- **Total GPU-Hours:** 13,920
- **Implementation Options:**
  - Single A40: 580 days (not feasible)
  - 10x A40s: 58 days (fits break period with buffer)
  - 20x A40s: 29 days (more comfortable timeline)
- **Expected Outcome:** Stable, domain-appropriate responses suitable for educational assessment
- **Risk Level:** Moderate - may still need refinement

#### Optimal (100x): Professional-Grade Quality
- **Total GPU-Hours:** 139,200
- **Implementation Options:**
  - 100x A40s: 5.8 days (intensive burst training)
  - 50x A40s: 11.6 days (more manageable)
  - Mixed GPU cluster: ~1 week intensive training
- **Expected Outcome:** Professional-grade educational assessment comparable to commercial LLM capabilities
- **Risk Level:** Low - provides comfortable margin for iteration

---

## Why This Matters for Next Trimester

### 1. Current Trajectory is Proven
We have demonstrated measurable improvement at each training stage:
- Stage 1 → 2: Learned basic language structure
- Stage 2 → 3: Learned topic relevance and context
- Stage 3 → Target: Need rubric-aligned assessment capabilities

### 2. Student Load Doubling
- **Current capacity planning:** Preparing for 2x expected student load
- **Quality requirement:** Cannot use models that generate children's stories for academic assessment
- **Timeline:** Models must be production-ready by trimester start

### 3. Critical Training Window
- **Trimester 1 2026:** Primary intensive training period
- **Timeline:** Must be production-ready before student load doubles
- **No second chances:** This is our one opportunity for major training iterations before deployment

### 4. Academic Credibility
- **Current Stage 2 outputs:** Would not pass HD panel review
- **Stage 3 outputs:** Show promise but need refinement
- **Target quality:** Must demonstrate clear superiority over zero-shot for project justification

---

## The Request

### Preferred Option (100x): Optimal Quality
- **Resources:** Access to 50-100 GPU cluster or equivalent Google Colab Pro resources
- **Duration:** Trimester 1 2026
- **Total Compute:** ~139,200 GPU-hours
- **Justification:** Each order-of-magnitude increase has produced qualitatively better results. This ensures production-ready quality with room for hyperparameter optimization.

### Minimum Viable Option (10x): Production Baseline
- **Resources:** Access to 10-20 GPU cluster
- **Duration:** Trimester 1 2026
- **Total Compute:** ~13,920 GPU-hours
- **Justification:** Sufficient to reach baseline production quality based on observed improvement trajectory.

---

## Evidence-Based Conclusion

The progression from "toooooo" → off-topic stories → contextual responses demonstrates an undeniable pattern: **our model quality is directly limited by available compute resources**. 

We are not asking for resources to explore whether more training helps - we have already proven it does. We are asking for resources to complete the progression from experimental outputs to production-ready educational assessment capabilities.

**The pattern is clear: minimal training → gibberish; moderate training → irrelevant narratives; extended training → on-topic content; intensive training → professional assessment quality.**

To deliver on our project goals and serve next trimester's student population, we need to complete this trajectory.

---

## Appendix: Technical Details

### Model Architecture
- **Base Model:** Llama 3.2-3B-Instruct
- **Dataset:** DREsS (Dataset for Rubric-based Essay Scoring)
- **Training Framework:** HuggingFace Transformers + PyTorch
- **Tokenization:** Completed and validated
- **Infrastructure:** Google Colab Pro / University GPU cluster

### Success Metrics
We will measure improvement using:
- Pearson/Spearman correlation with human scoring
- Cohen's Kappa for inter-rater reliability
- BERT Score for semantic similarity
- Judge metrics (relevance, accuracy, faithfulness, rubric alignment)
- Qualitative review of output appropriateness

### Risk Mitigation
- **Dual-track approach:** Zero-shot system as fallback
- **Incremental validation:** Checkpoint evaluation every 1,000 GPU-hours
- **Documentation:** Comprehensive training logs for future handover

---

**Prepared for:** Dr. Amin Atkin (Product Owner), Nebula Alam (Mentor)  
**Project Repository:** aaie-model-lab  
**Contact:** David, LLM Development Stream Lead