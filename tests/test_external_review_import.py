from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from tools import import_external_review as IMPORT

ROOT = Path(__file__).parents[1]


def write_json(path: Path, value: dict) -> Path:
    path.write_text(
        json.dumps(value, indent=2) + "\n",
        encoding="utf-8",
    )
    return path


def valid_clinical() -> dict:
    record = copy.deepcopy(IMPORT.load_json(ROOT / "P3_1_EXTERNAL_CLINICAL_SIGNOFF.json"))

    record["status"] = "approved-external-review"
    record["independentReviewer"]["name"] = "Dr Jamie Smith"
    record["independentReviewer"]["qualification"] = "Clinical Psychologist"
    record["independentReviewer"]["registrationOrCredential"] = "PSY0000000001"
    record["independentReviewer"]["areasOfExpertise"] = ["clinical neuroscience"]

    record["reviewDate"] = "2026-08-22"
    record["reviewedConceptCount"] = len(record["sampleConceptIds"])

    record["conceptDecisions"] = [
        {
            "conceptId": concept_id,
            "decision": "APPROVE",
            "comments": None,
            "requestedChanges": [],
        }
        for concept_id in record["sampleConceptIds"]
    ]

    findings = record["globalFindings"]

    findings["evidenceWeightingAppropriate"] = True
    findings["biomarkerLanguageAppropriate"] = True
    findings["traumaClaimsNonDeterministic"] = True
    findings["emdrEfficacyMechanismDistinctionAppropriate"] = True
    findings["contestedTheoryBoundariesAppropriate"] = True
    findings["diagnosticOverreachControlled"] = True
    findings["materialClinicalSafetyConcerns"] = False

    record["finalRecommendation"] = "APPROVE"
    record["signatureOrElectronicAcknowledgement"] = "Jamie Smith 22/08/2026"
    record["gateSatisfied"] = True

    return record


def valid_legal() -> dict:
    record = copy.deepcopy(IMPORT.load_json(ROOT / "P8_EXTERNAL_LEGAL_SIGNOFF.json"))

    record["status"] = "approved-external-review"
    record["independentReviewer"]["name"] = "Alex Morgan"
    record["independentReviewer"]["qualification"] = "Australian Solicitor"
    record["independentReviewer"]["practisingCertificateOrCredential"] = "QLD-LAW-000001"

    record["reviewDate"] = "2026-08-22"

    for key in record["scope"]:
        record["scope"][key] = True

    record["findings"]["materialLegalConcerns"] = False
    record["findings"]["requiredChanges"] = []

    record["finalRecommendation"] = "APPROVE"
    record["signatureOrElectronicAcknowledgement"] = "Alex Morgan 22/08/2026"
    record["gateSatisfied"] = True

    return record


def test_valid_completed_clinical_review_passes(tmp_path: Path):
    returned = write_json(
        tmp_path / "clinical.json",
        valid_clinical(),
    )

    result = IMPORT.validate_returned(
        ROOT,
        "clinical",
        returned,
    )

    assert result["valid"] is True
    assert result["issues"] == []
    assert result["snapshotIntegrity"]["valid"] is True


def test_valid_completed_legal_review_passes(tmp_path: Path):
    returned = write_json(
        tmp_path / "legal.json",
        valid_legal(),
    )

    result = IMPORT.validate_returned(
        ROOT,
        "legal",
        returned,
    )

    assert result["valid"] is True
    assert result["issues"] == []
    assert result["snapshotIntegrity"]["valid"] is True


def test_changed_snapshot_digest_is_rejected(tmp_path: Path):
    record = valid_clinical()
    record["reviewSnapshot"]["digest"] = "0" * 64

    returned = write_json(
        tmp_path / "clinical.json",
        record,
    )

    result = IMPORT.validate_returned(
        ROOT,
        "clinical",
        returned,
    )

    assert result["valid"] is False
    assert any("reviewSnapshot" in issue for issue in result["issues"])


def test_missing_clinical_decision_is_rejected(tmp_path: Path):
    record = valid_clinical()
    record["conceptDecisions"].pop()
    record["reviewedConceptCount"] -= 1

    returned = write_json(
        tmp_path / "clinical.json",
        record,
    )

    result = IMPORT.validate_returned(
        ROOT,
        "clinical",
        returned,
    )

    assert result["valid"] is False
    assert any("clinical concept decisions" in issue.lower() for issue in result["issues"])


def test_substantive_clinical_decision_is_rejected(tmp_path: Path):
    record = valid_clinical()
    record["conceptDecisions"][0]["decision"] = "REQUIRES SUBSTANTIVE REVISION"

    returned = write_json(
        tmp_path / "clinical.json",
        record,
    )

    result = IMPORT.validate_returned(
        ROOT,
        "clinical",
        returned,
    )

    assert result["valid"] is False
    assert any("not release-approved" in issue for issue in result["issues"])


def test_material_clinical_safety_concern_is_rejected(tmp_path: Path):
    record = valid_clinical()
    record["globalFindings"]["materialClinicalSafetyConcerns"] = True

    returned = write_json(
        tmp_path / "clinical.json",
        record,
    )

    result = IMPORT.validate_returned(
        ROOT,
        "clinical",
        returned,
    )

    assert result["valid"] is False
    assert any("clinical safety" in issue.lower() for issue in result["issues"])


def test_incomplete_legal_scope_is_rejected(tmp_path: Path):
    record = valid_legal()
    record["scope"]["acknowledgementDesign"] = False

    returned = write_json(
        tmp_path / "legal.json",
        record,
    )

    result = IMPORT.validate_returned(
        ROOT,
        "legal",
        returned,
    )

    assert result["valid"] is False
    assert any("acknowledgementDesign" in issue for issue in result["issues"])


def test_material_legal_concern_is_rejected(tmp_path: Path):
    record = valid_legal()
    record["findings"]["materialLegalConcerns"] = True

    returned = write_json(
        tmp_path / "legal.json",
        record,
    )

    result = IMPORT.validate_returned(
        ROOT,
        "legal",
        returned,
    )

    assert result["valid"] is False
    assert any("material legal concerns" in issue.lower() for issue in result["issues"])


def test_placeholder_reviewer_identity_is_rejected(tmp_path: Path):
    record = valid_clinical()
    record["independentReviewer"]["name"] = "Independent Reviewer"

    returned = write_json(
        tmp_path / "clinical.json",
        record,
    )

    result = IMPORT.validate_returned(
        ROOT,
        "clinical",
        returned,
    )

    assert result["valid"] is False
    assert any("placeholder" in issue.lower() for issue in result["issues"])


def test_apply_requires_manual_independence_confirmation(
    tmp_path: Path,
):
    returned = write_json(
        tmp_path / "clinical.json",
        valid_clinical(),
    )

    validation = IMPORT.validate_returned(
        ROOT,
        "clinical",
        returned,
    )

    assert validation["valid"] is True

    with pytest.raises(
        RuntimeError,
        match="explicit operator confirmation",
    ):
        IMPORT.apply_returned(
            ROOT,
            "clinical",
            returned,
            validation,
            False,
        )
