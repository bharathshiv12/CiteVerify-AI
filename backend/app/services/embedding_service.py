"""
Service: Embedding Service
Responsibility:
    Computes semantic vector representations or normalized token-level TF-IDF
    similarities for claims and candidate evidence passages to rank passages
    by relevance without requiring heavyweight ML dependencies by default.

Inputs:
    - query_text (str): Claim text to rank against.
    - passages (List[str]): Candidate evidence passages.

Outputs:
    - List[float]: Normalized similarity scores [0.0, 1.0] corresponding to each passage.
"""
import re
import math
from typing import List, Set, Dict

# Standard English stop words
STOP_WORDS: Set[str] = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are",
    "aren't", "as", "at", "be", "because", "been", "before", "being", "below", "between", "both",
    "but", "by", "can't", "cannot", "could", "couldn't", "did", "didn't", "do", "does", "doesn't",
    "doing", "don't", "down", "during", "each", "few", "for", "from", "further", "had", "hadn't",
    "has", "hasn't", "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here",
    "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i", "i'd", "i'll",
    "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's", "its", "itself", "let's",
    "me", "more", "most", "mustn't", "my", "myself", "no", "nor", "not", "of", "off", "on", "once",
    "only", "or", "other", "ought", "our", "ours", "ourselves", "out", "over", "own", "same", "shan't",
    "she", "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", "such", "than", "that",
    "that's", "the", "their", "theirs", "them", "themselves", "then", "there", "there's", "these",
    "they", "they'd", "they'll", "they're", "they've", "this", "those", "through", "to", "too",
    "under", "until", "up", "very", "was", "wasn't", "we", "we'd", "we'll", "we're", "we've", "were",
    "weren't", "what", "what's", "when", "when's", "where", "where's", "which", "while", "who", "who's",
    "whom", "why", "why's", "with", "won't", "would", "wouldn't", "you", "you'd", "you'll", "you're",
    "you've", "your", "yours", "yourself", "yourselves"
}

TOKEN_PATTERN = re.compile(r"\b[A-Za-z0-9_]{2,}\b")


def tokenize(text: str) -> List[str]:
    """Tokenize and remove stop words."""
    tokens = TOKEN_PATTERN.findall(text.lower())
    return [t for t in tokens if t not in STOP_WORDS]


def compute_similarities(query_text: str, passages: List[str]) -> List[float]:
    """
    Computes cosine similarity between query and candidate passages using TF-IDF.
    Returns a float in range [0.0, 1.0] for each passage.
    """
    if not passages:
        return []

    query_tokens = tokenize(query_text)
    if not query_tokens:
        # Fallback to character overlap if all were stop words or short symbols
        raw_words = query_text.lower().split()
        query_tokens = [w for w in raw_words if len(w) > 1]
        if not query_tokens:
            return [0.0] * len(passages)

    all_docs_tokens = [query_tokens] + [tokenize(p) for p in passages]
    total_docs = len(all_docs_tokens)

    # Document Frequency (DF)
    doc_freq: Dict[str, int] = {}
    for tokens in all_docs_tokens:
        for t in set(tokens):
            doc_freq[t] = doc_freq.get(t, 0) + 1

    # Inverse Document Frequency (IDF) with smoothing
    idf: Dict[str, float] = {}
    for token, df in doc_freq.items():
        idf[token] = math.log((1 + total_docs) / (1 + df)) + 1.0

    def compute_tfidf_vector(tokens: List[str]) -> Dict[str, float]:
        if not tokens:
            return {}
        tf: Dict[str, float] = {}
        for t in tokens:
            tf[t] = tf.get(t, 0.0) + 1.0
        # Term frequency normalization
        doc_len = len(tokens)
        vector: Dict[str, float] = {}
        for t, count in tf.items():
            vector[t] = (count / doc_len) * idf.get(t, 1.0)
        return vector

    query_vec = compute_tfidf_vector(query_tokens)
    query_norm = math.sqrt(sum(v * v for v in query_vec.values()))

    scores: List[float] = []
    for passage in passages:
        passage_tokens = tokenize(passage)
        if not passage_tokens:
            scores.append(0.0)
            continue

        p_vec = compute_tfidf_vector(passage_tokens)
        p_norm = math.sqrt(sum(v * v for v in p_vec.values()))

        if query_norm == 0.0 or p_norm == 0.0:
            scores.append(0.0)
            continue

        # Cosine similarity dot product
        dot_product = sum(query_vec[t] * p_vec[t] for t in query_vec if t in p_vec)
        cosine_sim = dot_product / (query_norm * p_norm)

        # Also add a slight bonus for exact phrase or shared numeric tokens
        query_numbers = set(re.findall(r"\b\d+(?:\.\d+)?%?\b", query_text))
        passage_numbers = set(re.findall(r"\b\d+(?:\.\d+)?%?\b", passage))
        numeric_overlap = query_numbers.intersection(passage_numbers)
        if numeric_overlap:
            cosine_sim = min(1.0, cosine_sim + 0.1 * len(numeric_overlap))

        # Clamp between 0.0 and 1.0
        scores.append(round(max(0.0, min(1.0, cosine_sim)), 4))

    return scores
