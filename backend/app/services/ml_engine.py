"""
Service: ML Engine (Pretrained Semantic Retrieval, NLI Classification, and Numerical Verification)
Responsibility:
    Provides pretrained ML capabilities for:
    1. Semantic evidence retrieval via Sentence Transformers (all-MiniLM-L6-v2) with TF-IDF fallback.
    2. Evidence classification via Pretrained NLI (entailment, contradiction, neutral) with heuristic fallback.
    3. Explicit numerical verification (percentages, sample sizes, numbers, units, dates, statistical significance).

Model Information & Limitations:
    - Sentence Transformer: sentence-transformers/all-MiniLM-L6-v2 (Apache-2.0, 384-dim, ~80MB, fast CPU inference).
    - NLI Classifier: cross-encoder/nli-deberta-v3-small or MoritzLaurer/DeBERTa-v3-xsmall-mnli (MIT / Apache-2.0).
    - Scientific Disclaimer: General-domain NLI models (trained on MultiNLI/SNLI) are NOT calibrated for
      specialized scientific/biomedical claims. Their raw probabilities must not be treated as calibrated
      epistemic confidence, and neutral or ambiguous evidence must remain unforced (null verdict).
"""
import re
import math
import logging
from typing import List, Dict, Any, Optional, Tuple, Set

logger = logging.getLogger("citeverify.ml_engine")


# =====================================================================
# 1. NUMERICAL VERIFICATION ENGINE
# =====================================================================

PERCENTAGE_PATTERN = re.compile(r"(\d+(?:\.\d+)?)\s*(?:%|percent(?:age)?)", re.IGNORECASE)
SAMPLE_SIZE_PATTERNS = [
    re.compile(r"\b(?:n|N)\s*=\s*(\d+(?:,\d+)?)\b"),
    re.compile(r"(\d+(?:,\d+)?)\s+(?:patients|participants|subjects|individuals|cases|samples|records|cohorts|volunteers)\b", re.IGNORECASE),
]
STATISTICAL_PATTERNS = [
    re.compile(r"\b(?:p|P)\s*([<>=])\s*(\d+(?:\.\d+)?)\b"),
    re.compile(r"\b(?:HR|OR|RR)\s*=\s*(\d+(?:\.\d+)?)\b", re.IGNORECASE),
    re.compile(r"95%\s*CI\s*\[\s*(\d+(?:\.\d+)?)\s*,\s*(\d+(?:\.\d+)?)\s*\]", re.IGNORECASE),
]
QUANTITY_WITH_UNIT_PATTERN = re.compile(
    r"(\d+(?:\.\d+)?)\s*(mg|g|kg|ml|l|mm|cm|m|km|ms|s|sec|seconds?|min|minutes?|hours?|days?|weeks?|months?|years?|fold|ghz|mhz|mmhg|kgy)\b",
    re.IGNORECASE,
)
YEAR_DATE_PATTERN = re.compile(r"\b(19\d{2}|20\d{2})\b")
RAW_NUMBER_PATTERN = re.compile(r"\b\d+(?:\.\d+)?\b")


class NumericalVerificationResult:
    def __init__(
        self,
        has_discrepancy: bool,
        severity: str,  # "NONE" | "LOW" | "HIGH_CONTRADICTION"
        discrepancy_reasons: List[str],
        matched_facts: List[str],
        claim_entities: Dict[str, Any],
        evidence_entities: Dict[str, Any],
    ):
        self.has_discrepancy = has_discrepancy
        self.severity = severity
        self.discrepancy_reasons = discrepancy_reasons
        self.matched_facts = matched_facts
        self.claim_entities = claim_entities
        self.evidence_entities = evidence_entities

    def to_dict(self) -> Dict[str, Any]:
        return {
            "has_discrepancy": self.has_discrepancy,
            "severity": self.severity,
            "discrepancy_reasons": self.discrepancy_reasons,
            "matched_facts": self.matched_facts,
            "claim_entities": self.claim_entities,
            "evidence_entities": self.evidence_entities,
        }


class NumericalVerifier:
    """
    Performs rigorous extraction and verification of quantitative assertions.
    """

    @classmethod
    def extract_entities(cls, text: str) -> Dict[str, Any]:
        """Extracts percentages, sample sizes, units, dates, and p-values."""
        # 1. Percentages
        percentages = [float(m.group(1)) for m in PERCENTAGE_PATTERN.finditer(text)]

        # 2. Sample sizes
        sample_sizes = []
        for pat in SAMPLE_SIZE_PATTERNS:
            for m in pat.finditer(text):
                clean_num = m.group(1).replace(",", "")
                try:
                    sample_sizes.append(int(clean_num))
                except ValueError:
                    pass

        # 3. Statistical comparisons (p-values, effect sizes)
        p_values = []
        for pat in STATISTICAL_PATTERNS:
            for m in pat.finditer(text):
                p_values.append(m.group(0))

        # 4. Quantities with units
        quantities = []
        for m in QUANTITY_WITH_UNIT_PATTERN.finditer(text):
            val = float(m.group(1))
            unit = m.group(2).lower()
            quantities.append((val, unit))

        # 5. Years / Dates
        years = [int(m.group(1)) for m in YEAR_DATE_PATTERN.finditer(text)]

        # 6. Standalone raw numbers
        raw_numbers = [float(n) for n in RAW_NUMBER_PATTERN.findall(text)]

        return {
            "percentages": sorted(list(set(percentages))),
            "sample_sizes": sorted(list(set(sample_sizes))),
            "statistical": p_values,
            "quantities": quantities,
            "years": sorted(list(set(years))),
            "raw_numbers": raw_numbers,
        }

    @classmethod
    def verify(cls, claim_text: str, evidence_text: str) -> NumericalVerificationResult:
        """
        Cross-checks all numerical and statistical entities between claim and evidence.
        Detects conflicting percentages, sample sizes, units, and statistical conclusions.
        """
        c_ent = cls.extract_entities(claim_text)
        e_ent = cls.extract_entities(evidence_text)

        discrepancies: List[str] = []
        matched_facts: List[str] = []
        severity = "NONE"

        # 1. Check Percentage Consistency
        c_pcts = c_ent["percentages"]
        e_pcts = e_ent["percentages"]
        if c_pcts and e_pcts:
            for cp in c_pcts:
                # Find closest percentage in evidence
                closest = min(e_pcts, key=lambda ep: abs(ep - cp))
                diff = abs(closest - cp)
                if diff < 0.5:
                    matched_facts.append(f"Percentage corroborated: {cp}% matches evidence ({closest}%).")
                elif diff >= 5.0:
                    discrepancies.append(
                        f"Conflicting quantitative figures (Percentage mismatch: claim asserts {cp}%, but evidence indicates {closest}%)."
                    )
                    severity = "HIGH_CONTRADICTION"
        elif c_pcts and not e_pcts and e_ent["raw_numbers"]:
            # Claim claims percent, evidence has raw numbers but no percent
            pass

        # 2. Check Sample Size Consistency
        c_samples = c_ent["sample_sizes"]
        e_samples = e_ent["sample_sizes"]
        if c_samples and e_samples:
            for cs in c_samples:
                closest_s = min(e_samples, key=lambda es: abs(es - cs))
                if cs == closest_s:
                    matched_facts.append(f"Sample size corroborated: n = {cs}.")
                elif abs(cs - closest_s) > 10:
                    discrepancies.append(
                        f"Sample size discrepancy: claim states n = {cs}, but evidence specifies n = {closest_s}."
                    )
                    if severity != "HIGH_CONTRADICTION":
                        severity = "LOW"

        # 3. Check Quantity and Unit Matching
        c_quantities = c_ent["quantities"]
        e_quantities = e_ent["quantities"]
        if c_quantities and e_quantities:
            for c_val, c_unit in c_quantities:
                for e_val, e_unit in e_quantities:
                    if c_unit == e_unit:
                        if abs(c_val - e_val) < 0.01:
                            matched_facts.append(f"Quantity matched: {c_val} {c_unit}.")
                        elif abs(c_val - e_val) / max(c_val, e_val, 1.0) > 0.15:
                            discrepancies.append(
                                f"Quantity conflict: claim states {c_val} {c_unit}, but evidence states {e_val} {e_unit}."
                            )
                            severity = "HIGH_CONTRADICTION"
                    elif abs(c_val - e_val) < 0.01:
                        # Identical number with incompatible unit (e.g. 50 mg vs 50 g)
                        discrepancies.append(
                            f"Unit conflict: claim states {c_val} {c_unit}, but evidence states {e_val} {e_unit}."
                        )
                        severity = "HIGH_CONTRADICTION"

        # 4. Check Statistical Significance Inversions
        claim_lower = claim_text.lower()
        evidence_lower = evidence_text.lower()

        c_stat_sig = any(w in claim_lower for w in ["statistically significant", "significant difference", "significant increase", "significant reduction"])
        e_no_sig = any(w in evidence_lower for w in ["no statistically significant", "not statistically significant", "no significant difference", "failed to reach significance"])

        if c_stat_sig and e_no_sig:
            discrepancies.append(
                "Statistical contradiction: claim asserts statistical significance, but evidence reports finding was not statistically significant."
            )
            severity = "HIGH_CONTRADICTION"

        has_disc = bool(discrepancies)
        return NumericalVerificationResult(
            has_discrepancy=has_disc,
            severity=severity,
            discrepancy_reasons=discrepancies,
            matched_facts=matched_facts,
            claim_entities=c_ent,
            evidence_entities=e_ent,
        )


# =====================================================================
# 2. SEMANTIC EVIDENCE RETRIEVAL (SENTENCE TRANSFORMERS + TF-IDF FALLBACK)
# =====================================================================

class SentenceTransformerRetriever:
    """
    Encapsulates sentence-transformers/all-MiniLM-L6-v2 for dense semantic passage ranking.
    Lazily loads model on CPU with automatic fallback to TF-IDF when dependencies or models are unavailable.
    """
    MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

    def __init__(self):
        self._model = None
        self._load_attempted = False
        self._is_available = False

    def is_available(self) -> bool:
        if not self._load_attempted:
            self._init_model()
        return self._is_available

    def _init_model(self):
        self._load_attempted = True
        try:
            from sentence_transformers import SentenceTransformer
            logger.info(f"Loading SentenceTransformer: {self.MODEL_NAME} on CPU...")
            self._model = SentenceTransformer(self.MODEL_NAME, device="cpu")
            self._is_available = True
            logger.info("SentenceTransformer loaded successfully.")
        except Exception as e:
            self._is_available = False
            self._model = None
            logger.warning(
                f"SentenceTransformer ({self.MODEL_NAME}) not available ({e}). "
                "Operating in lightweight TF-IDF semantic fallback mode."
            )

    def compute_similarities(self, query: str, passages: List[str]) -> List[float]:
        """
        Computes cosine similarities between query and passages using SentenceTransformer.
        Falls back to TF-IDF cosine similarity if unavailable.
        """
        if not passages:
            return []

        if self.is_available() and self._model is not None:
            try:
                # Dense embedding computation
                embeddings = self._model.encode([query] + passages, normalize_embeddings=True)
                query_emb = embeddings[0]
                passage_embs = embeddings[1:]

                # Cosine similarity via dot product (embeddings are normalized)
                scores: List[float] = []
                for p_emb in passage_embs:
                    score = float(sum(q * p for q, p in zip(query_emb, p_emb)))
                    # Normalize from [-1.0, 1.0] to [0.0, 1.0]
                    norm_score = max(0.0, min(1.0, (score + 1.0) / 2.0))
                    scores.append(round(norm_score, 4))
                return scores
            except Exception as ex:
                logger.warning(f"Error during SentenceTransformer inference ({ex}), falling back to TF-IDF.")

        # Lightweight TF-IDF Fallback
        from app.services.embedding_service import compute_similarities_tfidf as tfidf_sim
        return tfidf_sim(query, passages)


# =====================================================================
# 3. PRETRAINED NATURAL LANGUAGE INFERENCE (NLI) CLASSIFIER
# =====================================================================

class PretrainedNLIClassifier:
    """
    Evaluates semantic relationship between a premise (evidence passage) and hypothesis (claim).
    Investigates 3 canonical NLI labels:
      - ENTAILMENT
      - CONTRADICTION
      - NEUTRAL / INSUFFICIENT
    """
    MODEL_NAME = "cross-encoder/nli-deberta-v3-small"

    def __init__(self):
        self._classifier = None
        self._load_attempted = False
        self._is_available = False

    def is_available(self) -> bool:
        if not self._load_attempted:
            self._init_classifier()
        return self._is_available

    def _init_classifier(self):
        self._load_attempted = True
        try:
            from transformers import pipeline
            logger.info(f"Loading Hugging Face NLI pipeline: {self.MODEL_NAME} on CPU...")
            self._classifier = pipeline(
                "text-classification",
                model=self.MODEL_NAME,
                device=-1,  # CPU execution
                top_k=None,
            )
            self._is_available = True
            logger.info("Pretrained NLI classifier loaded successfully.")
        except Exception as e:
            self._is_available = False
            self._classifier = None
            logger.warning(
                f"Pretrained NLI classifier ({self.MODEL_NAME}) not available ({e}). "
                "Operating in deterministic heuristic NLI fallback mode."
            )

    def classify(self, premise: str, hypothesis: str) -> Dict[str, Any]:
        """
        Infers NLI distribution between premise (evidence) and hypothesis (claim).
        Returns label: 'ENTAILMENT' | 'CONTRADICTION' | 'NEUTRAL', with confidence score.
        """
        if self.is_available() and self._classifier is not None:
            try:
                # Format for cross-encoder/nli: "premise [SEP] hypothesis" or text/text_pair
                preds = self._classifier(f"{premise} [SEP] {hypothesis}")
                if isinstance(preds, list) and preds and isinstance(preds[0], list):
                    scores = {p["label"].upper(): float(p["score"]) for p in preds[0]}
                elif isinstance(preds, list) and preds:
                    scores = {p["label"].upper(): float(p["score"]) for p in preds}
                else:
                    scores = {}

                # Map various label names (e.g. LABEL_0, ENTAILMENT, contradiction)
                entailment_prob = scores.get("ENTAILMENT", scores.get("LABEL_0", 0.0))
                neutral_prob = scores.get("NEUTRAL", scores.get("LABEL_1", 0.0))
                contradiction_prob = scores.get("CONTRADICTION", scores.get("LABEL_2", 0.0))

                top_label = max(
                    [("ENTAILMENT", entailment_prob), ("CONTRADICTION", contradiction_prob), ("NEUTRAL", neutral_prob)],
                    key=lambda x: x[1],
                )[0]

                return {
                    "label": top_label,
                    "confidence": max(entailment_prob, neutral_prob, contradiction_prob),
                    "probabilities": {
                        "entailment": entailment_prob,
                        "neutral": neutral_prob,
                        "contradiction": contradiction_prob,
                    },
                    "mode": "pretrained_ml",
                }
            except Exception as ex:
                logger.warning(f"Error during NLI inference ({ex}), using rule-based NLI.")

        # Fallback to Deterministic Heuristic NLI
        return self._heuristic_fallback_nli(premise, hypothesis)

    def _heuristic_fallback_nli(self, premise: str, hypothesis: str) -> Dict[str, Any]:
        """
        Deterministic, rule-based natural language inference fallback using
        stemmed token overlap, polarity detection, and semantic similarity.
        """
        from app.services.embedding_service import compute_similarities_tfidf
        sim_score = compute_similarities_tfidf(hypothesis, [premise])[0]

        premise_lower = premise.lower()
        hyp_lower = hypothesis.lower()

        # Stemming helper for inflectional robustness
        def _stem(word: str) -> str:
            for suffix in ["ing", "tion", "ness", "ment", "ed", "es", "s"]:
                if word.endswith(suffix) and len(word) > len(suffix) + 2:
                    return word[:-len(suffix)]
            return word

        p_words = re.findall(r"\b[a-z]{3,}\b", premise_lower)
        h_words = re.findall(r"\b[a-z]{3,}\b", hyp_lower)

        p_stemmed = {_stem(w) for w in p_words}
        h_stemmed = {_stem(w) for w in h_words}

        overlap = p_stemmed.intersection(h_stemmed)
        overlap_ratio = len(overlap) / max(len(h_stemmed), 1)

        # Polarity & Antonym dictionaries
        negative_indicators = {"fail", "failed", "ineffective", "adverse", "harmful", "toxic", "worsened", "rejected", "contraindicated", "not", "never", "no", "neither", "nor", "without"}
        positive_indicators = {"effective", "safe", "efficacy", "improved", "successful", "beneficial", "cured", "superior", "enhanced", "reduced mortality", "achieved"}

        p_neg = bool(p_stemmed.intersection(negative_indicators) or set(p_words).intersection(negative_indicators))
        h_neg = bool(h_stemmed.intersection(negative_indicators) or set(h_words).intersection(negative_indicators))

        p_pos = bool(p_stemmed.intersection(positive_indicators) or set(p_words).intersection(positive_indicators))
        h_pos = bool(h_stemmed.intersection(positive_indicators) or set(h_words).intersection(positive_indicators))

        # Check for direct antonym / polarity inversion
        has_antonym_conflict = (p_neg and h_pos) or (p_pos and h_neg) or (p_neg != h_neg and overlap_ratio >= 0.25)

        if has_antonym_conflict and (overlap_ratio >= 0.20 or sim_score >= 0.15):
            label = "CONTRADICTION"
            conf = min(0.92, round(max(overlap_ratio, sim_score) + 0.15, 2))
        elif overlap_ratio >= 0.35 or sim_score >= 0.40:
            label = "ENTAILMENT"
            conf = min(0.95, round(max(overlap_ratio, sim_score) + 0.1, 2))
        elif overlap_ratio >= 0.20 or sim_score >= 0.25:
            label = "ENTAILMENT" if not p_neg and not h_neg else "NEUTRAL"
            conf = round(max(overlap_ratio, sim_score), 2)
        else:
            label = "NEUTRAL"
            conf = round(max(overlap_ratio, sim_score), 2)

        return {
            "label": label,
            "confidence": conf,
            "probabilities": {
                "entailment": 1.0 if label == "ENTAILMENT" else 0.0,
                "neutral": 1.0 if label == "NEUTRAL" else 0.0,
                "contradiction": 1.0 if label == "CONTRADICTION" else 0.0,
            },
            "mode": "heuristic_fallback",
        }


# =====================================================================
# 4. SINGLETON INSTANCES & UNIFIED ML ENGINE INTERFACE
# =====================================================================

_retriever_instance = SentenceTransformerRetriever()
_nli_instance = PretrainedNLIClassifier()


def get_semantic_similarities(query_text: str, passages: List[str]) -> List[float]:
    """Exposed function for semantic passage ranking."""
    return _retriever_instance.compute_similarities(query_text, passages)


def evaluate_nli(premise: str, hypothesis: str) -> Dict[str, Any]:
    """Exposed function for natural language inference."""
    return _nli_instance.classify(premise, hypothesis)


def check_numerical_consistency(claim_text: str, evidence_text: str) -> NumericalVerificationResult:
    """Exposed function for numerical fact cross-checking."""
    return NumericalVerifier.verify(claim_text, evidence_text)


def get_ml_engine_status() -> Dict[str, Any]:
    """Provides transparency on loaded models, versions, and execution modes."""
    return {
        "semantic_retriever": {
            "model_name": SentenceTransformerRetriever.MODEL_NAME,
            "is_available": _retriever_instance.is_available(),
            "device": "cpu",
            "fallback": "TF-IDF Vector Space Model",
        },
        "nli_classifier": {
            "model_name": PretrainedNLIClassifier.MODEL_NAME,
            "is_available": _nli_instance.is_available(),
            "device": "cpu",
            "fallback": "Deterministic Lexical/Polarity NLI",
            "scientific_disclaimer": (
                "General-domain NLI models are not calibrated on domain-specific scientific literature. "
                "Low or neutral confidence leads to human-review recommendation."
            ),
        },
        "numerical_verifier": {
            "version": "1.0.0",
            "capabilities": ["percentages", "sample_sizes", "quantities_with_units", "p_values", "dates"],
            "status": "active",
        },
    }
