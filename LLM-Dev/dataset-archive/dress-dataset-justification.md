# Dataset Selection Justification

**Task**: 5.3 - Dataset Research  
**Author**: David  
**Date**: December 9, 2025

---

## Selected Dataset: DREsS

**DREsS** (Dataset for Rubric-based Essay Scoring on EFL Writing)  
**Source**: Yoo et al. (2024), KAIST  
**Size**: 8,321 usable essays (after cleaning)

### Why DREsS?

1. **Native Rubric Structure** - Multi-dimensional scoring (Content, Organization, Language) matches project requirements exactly
2. **Appropriate Scale** - 8,321 essays sufficient for mini-LLM (<3B parameters) fine-tuning
3. **Privacy-Compliant** - Pre-anonymized data supports local deployment requirements
4. **Educational Authenticity** - Real student essays (EFL) with professional annotations
5. **Technical Compatibility** - Clean conversion to instruction-completion format for Qwen 2.5-3B

---

## Dataset Composition

| Component | Count | Use |
|-----------|-------|-----|
| Train | 6,656 (80%) | Model training |
| Validation | 832 (10%) | Hyperparameter tuning |
| Test | 833 (10%) | Final evaluation |

**Total**: 8,321 essays with complete rubric scores

---

## Alternatives Considered

| Dataset | Rejected Because |
|---------|------------------|
| ASAP | Single holistic score only - no rubric dimensions |
| CommonLit | Readability scoring - wrong task |
| Kaggle Feedback Prize | Inconsistent annotations, privacy concerns |

---

## Data Access

**Note**: The DREsS dataset is NOT included in this repository for ethical reasons.

### How to Access DREsS

The dataset is available through a formal access request process documented in `datasets/raw/README.docx`:

1. Complete the data access request form provided by KAIST
2. Provide your academic affiliation and intended research use
3. Obtain consent from the dataset authors

**Expected Timeline**: Using the current process i was granted approval on the same day

### Why Dataset Not Included in Repository


- Leadership decision was it was more approriate to provide instructions about gaining access instead of the dataset in the repo

Students and researchers should have no difficulty obtaining access by following the standard procedure outlined in the dataset README documentation, assuming there are no changes to the process.

---

## Technical Details

- **Tokenizer**: Qwen/Qwen2.5-3B-Instruct (151,643 vocab)
- **Max Length**: 2,048 tokens
- **Format**: Instruction-completion pairs
- **Processing Pipeline**: See `notebooks/DREsS_Tokenization_Pipeline.ipynb`

---

## Conclusion

DREsS provides optimal foundation for rubric-based assessment: native multi-dimensional scoring, appropriate scale, privacy compliance, and technical compatibility with our 3B parameter model architecture.# Dataset Selection Justification

**Task**: 5.3 - Dataset Research  
**Author**: David  
**Date**: December 9, 2025

---

## Selected Dataset: DREsS

**DREsS** (Dataset for Rubric-based Essay Scoring on EFL Writing)  
**Source**: Yoo et al. (2024), KAIST  
**Size**: 8,321 usable essays (after cleaning)

### Why DREsS?

1. **Native Rubric Structure** - Multi-dimensional scoring (Content, Organization, Language) matches project requirements exactly
2. **Appropriate Scale** - 8,321 essays sufficient for mini-LLM (<3B parameters) fine-tuning
3. **Privacy-Compliant** - Pre-anonymized data supports local deployment requirements
4. **Educational Authenticity** - Real student essays (EFL) with professional annotations
5. **Technical Compatibility** - Clean conversion to instruction-completion format for Qwen 2.5-3B

---

## Dataset Composition

| Component | Count | Use |
|-----------|-------|-----|
| Train | 6,656 (80%) | Model training |
| Validation | 832 (10%) | Hyperparameter tuning |
| Test | 833 (10%) | Final evaluation |

**Total**: 8,321 essays with complete rubric scores

---

## Alternatives Considered

| Dataset | Rejected Because |
|---------|------------------|
| ASAP | Single holistic score only - no rubric dimensions |
| CommonLit | Readability scoring - wrong task |
| Kaggle Feedback Prize | Inconsistent annotations, privacy concerns |

---

## Data Access

**Note**: The DREsS dataset is NOT included in this repository for ethical reasons.

### How to Access DREsS

The dataset is available through a formal access request process documented in `datasets/raw/README.docx`:

1. Complete the data access request form provided by KAIST
2. Provide your academic affiliation and intended research use
3. Obtain consent from the dataset authors

**Expected Timeline**: Access is typically granted within 1-2 weeks for students and academic researchers.

### Why Dataset Not Included in Repository

- Ethical considerations regarding student essay data
- Licensing restrictions require individual user consent
- Each user must agree to usage terms directly with KAIST

Students and researchers should have no difficulty obtaining access by following the standard procedure outlined in the dataset README documentation.

---

## Technical Details

- **Tokenizer**: Qwen/Qwen2.5-3B-Instruct (151,643 vocab)
- **Max Length**: 2,048 tokens
- **Format**: Instruction-completion pairs
- **Processing Pipeline**: See `notebooks/DREsS_Tokenization_Pipeline.ipynb`

---

## Conclusion

DREsS provides optimal foundation for rubric-based assessment: native multi-dimensional scoring, appropriate scale, privacy compliance, and technical compatibility with our 3B parameter model architecture.