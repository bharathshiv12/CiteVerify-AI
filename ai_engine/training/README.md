# AI Engine Training Directory (Optional ML Track)

This directory provides scaffolding for optional fine-tuning and classification models (e.g. claim-worthiness classification, NLI 3-way/5-way classifiers).

---

## 1. Hackathon MVP Strategy
- **MVP Default:** The production path uses **zero-shot LLM structured inference** (via Google Gemini free tier) combined with semantic cosine passage ranking. This requires ₹0 compute and no GPU training overhead.
- **Optional ML Experiments:** If time permits and GPU compute is available, lightweight classifier heads or SetFit models can be trained and evaluated using configs in `configs/` and exploration notebooks in `notebooks/`.

---

## 2. Directory Structure
- `configs/`: YAML/JSON hyperparameters and dataset split configurations.
- `notebooks/`: Jupyter notebooks for exploratory data analysis, prompt experiments, and error analysis.

