"""
Service: Embedding Service
Owner: Agent 3 (AI/ML Engineer)
Responsibility:
    Computes semantic vector representations for claims and candidate evidence passages
    to rank passages by relevance and filter out irrelevant excerpts.

Inputs:
    - query_text (str): Claim text to rank against.
    - passages (List[str]): Candidate evidence passages.

Outputs:
    - List[float]: Cosine similarity scores corresponding to each passage.
"""
from typing import List


def compute_similarities(query_text: str, passages: List[str]) -> List[float]:
    """
    Ranks passages against query using local sentence-transformers or cloud embedding.
    Raises NotImplementedError until Agent 3 implements embedding service.
    """
    raise NotImplementedError("compute_similarities not implemented yet (Assigned to Agent 3).")

