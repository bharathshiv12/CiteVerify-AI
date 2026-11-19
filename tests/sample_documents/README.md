# Sample Open-Access Test Documents

This directory contains instructions and metadata for obtaining verified, open-access academic papers for end-to-end integration testing.

> [!CAUTION]
> **No Fake or Copyrighted Documents:**
> Never fabricate research papers or commit proprietary/paywalled PDFs to this repository.

---

## Recommended Benchmark Papers (Open Access)

1. **Transformer Architecture:**
   - **Title:** Attention Is All You Need
   - **Authors:** Vaswani et al.
   - **Year:** 2017
   - **ArXiv DOI:** `10.48550/arXiv.1706.03762`
   - **URL:** https://arxiv.org/pdf/1706.03762.pdf
   - **License:** Open Access / arXiv distribution license
   - **Use Case:** Tests numeric citations `[1]`, empirical translation BLEU claims, and multi-page text extraction.

2. **CRISPR-Cas9 Gene Editing:**
   - **Title:** The new frontier of genome engineering with CRISPR-Cas9
   - **Authors:** Doudna, J. A., & Charpentier, E.
   - **Year:** 2014
   - **DOI:** `10.1126/science.1258096`
   - **Use Case:** Tests biomedical literature parsing and Europe PMC integration.

---

## Instructions for Local Testing
To test end-to-end pipeline execution locally:
1. Download `attention_is_all_you_need.pdf` from arXiv.
2. Place the file in this directory as `sample_benchmark.pdf` (this folder's PDFs are gitignored).
3. Run the upload and verification pipeline via `scripts/dev_start.py` or frontend UI.

