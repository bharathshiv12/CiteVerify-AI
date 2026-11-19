# AI Engine Evaluation & Benchmarking

This directory contains evaluation datasets and scoring scripts to compute real accuracy, precision, recall, and Macro-F1 across the 5 canonical verdicts (`SUPPORTED`, `PARTLY_SUPPORTED`, `UNSUPPORTED`, `CONTRADICTORY`, `POTENTIALLY_OUTDATED`).

---

## 1. Ground Truth Benchmark Dataset
- Stored in `ai_engine/data/benchmark_samples.json`.
- Contains 20–30 real academic claim-evidence pairs with verified ground-truth verdicts.
- **Never fabricate benchmark samples or accuracy numbers.**

---

## 2. Running Evaluation
```bash
python ai_engine/evaluation/evaluate.py
```
Outputs a confusion matrix and classification report reporting real metrics for the live presentation.

