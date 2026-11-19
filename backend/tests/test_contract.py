"""
Contract drift test.
Validates that backend Pydantic enumerations and schemas match canonical contracts/schemas/.
"""
import os
import json
import pytest

from app.schemas.enums import (
    VerificationVerdict,
    ProcessingStatus,
    VerificationState,
    EvidenceLevel,
    RetrievalStatus,
    PipelineStage,
)


@pytest.fixture
def canonical_enums():
    # Resolve relative to repo root
    current_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.abspath(os.path.join(current_dir, "..", ".."))
    enums_path = os.path.join(repo_root, "contracts", "schemas", "enums.json")
    with open(enums_path, "r", encoding="utf-8") as f:
        return json.load(f)["definitions"]


def test_verification_verdict_matches_canonical(canonical_enums):
    expected = set(canonical_enums["VerificationVerdict"]["enum"])
    actual = {e.value for e in VerificationVerdict}
    assert actual == expected, f"VerificationVerdict drift detected: {actual ^ expected}"


def test_processing_status_matches_canonical(canonical_enums):
    expected = set(canonical_enums["ProcessingStatus"]["enum"])
    actual = {e.value for e in ProcessingStatus}
    assert actual == expected, f"ProcessingStatus drift detected: {actual ^ expected}"


def test_verification_state_matches_canonical(canonical_enums):
    expected = set(canonical_enums["VerificationState"]["enum"])
    actual = {e.value for e in VerificationState}
    assert actual == expected, f"VerificationState drift detected: {actual ^ expected}"


def test_evidence_level_matches_canonical(canonical_enums):
    expected = set(canonical_enums["EvidenceLevel"]["enum"])
    actual = {e.value for e in EvidenceLevel}
    assert actual == expected, f"EvidenceLevel drift detected: {actual ^ expected}"


def test_retrieval_status_matches_canonical(canonical_enums):
    expected = set(canonical_enums["RetrievalStatus"]["enum"])
    actual = {e.value for e in RetrievalStatus}
    assert actual == expected, f"RetrievalStatus drift detected: {actual ^ expected}"


def test_pipeline_stage_matches_canonical(canonical_enums):
    expected = set(canonical_enums["PipelineStage"]["enum"])
    actual = {e.value for e in PipelineStage}
    assert actual == expected, f"PipelineStage drift detected: {actual ^ expected}"

