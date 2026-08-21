from __future__ import annotations

import importlib.util
import json
import shutil
from pathlib import Path

from tools import reviewer_snapshot as SNAPSHOT

ROOT = Path(__file__).parents[1]

SPEC = importlib.util.spec_from_file_location(
    "public_v1_gate",
    ROOT / "tools" / "public_v1_gate.py",
)
assert SPEC and SPEC.loader
GATE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(GATE)

GOVERNANCE_FILES = (
    "P8_ACKNOWLEDGEMENT_GATE_REPORT.json",
    "P3_2_EVIDENCE_GOVERNANCE_REPORT.json",
    "P3_1_EXTERNAL_CLINICAL_SIGNOFF.json",
    "P8_LEGAL_LICENSING_GOVERNANCE_REPORT.json",
    "P8_EXTERNAL_LEGAL_SIGNOFF.json",
    "RUNTIME_QA_REPORT.json",
)


def copy_relative(tmp_path: Path, relative: str) -> None:
    source = ROOT / relative
    target = tmp_path / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def copy_fixture(tmp_path: Path) -> Path:
    required = {
        "app/data/release-manifest.json",
        *GOVERNANCE_FILES,
    }

    for scope in ("clinical", "legal"):
        required.update(SNAPSHOT.scope_paths(ROOT, scope))

    for relative in sorted(required):
        copy_relative(tmp_path, relative)

    return tmp_path


def write_json(path: Path, value: dict) -> None:
    path.write_text(
        json.dumps(value, indent=2) + "\n",
        encoding="utf-8",
    )


def approve_clinical(root: Path) -> None:
    path = root / "P3_1_EXTERNAL_CLINICAL_SIGNOFF.json"
    record = json.loads(path.read_text(encoding="utf-8"))

    record["status"] = "approved-external-review"
    record["independentReviewer"]["name"] = "Independent Reviewer"
    record["independentReviewer"]["qualification"] = "Clinical Psychologist"
    record["reviewDate"] = "2026-08-21"
    record["reviewedConceptCount"] = len(record["sampleConceptIds"])
    record["conceptDecisions"] = [
        {
            "conceptId": concept_id,
            "decision": "APPROVE",
        }
        for concept_id in record["sampleConceptIds"]
    ]

    record["globalFindings"] = {
        "evidenceWeightingAppropriate": True,
        "biomarkerLanguageAppropriate": True,
        "traumaClaimsNonDeterministic": True,
        "emdrEfficacyMechanismDistinctionAppropriate": True,
        "contestedTheoryBoundariesAppropriate": True,
        "diagnosticOverreachControlled": True,
        "materialClinicalSafetyConcerns": False,
        "comments": None,
    }
    record["finalRecommendation"] = "APPROVE"
    record["signatureOrElectronicAcknowledgement"] = "signed"
    record["gateSatisfied"] = True

    write_json(path, record)


def approve_legal(root: Path) -> None:
    path = root / "P8_EXTERNAL_LEGAL_SIGNOFF.json"
    record = json.loads(path.read_text(encoding="utf-8"))

    record["status"] = "approved-external-review"
    record["independentReviewer"]["name"] = "Independent Lawyer"
    record["independentReviewer"]["qualification"] = "Australian Solicitor"
    record["reviewDate"] = "2026-08-21"

    for key in record["scope"]:
        record["scope"][key] = True

    record["findings"]["materialLegalConcerns"] = False
    record["finalRecommendation"] = "APPROVE"
    record["signatureOrElectronicAcknowledgement"] = "signed"
    record["gateSatisfied"] = True

    write_json(path, record)


def test_current_release_candidate_is_truthfully_blocked():
    report = GATE.evaluate(ROOT)

    assert report["publicV1Status"] == "BLOCKED"
    assert "external-clinical-review" in report["blockers"]
    assert "external-legal-review" in report["blockers"]
    assert report["gates"]["acknowledgement-gate"]["satisfied"] is True
    assert report["gates"]["evidence-governance"]["satisfied"] is True
    assert report["gates"]["runtime-regression"]["satisfied"] is True
    assert report["gates"]["external-clinical-review"]["snapshotIntegrity"]["valid"] is True
    assert report["gates"]["external-legal-review"]["snapshotIntegrity"]["valid"] is True
    assert report["contradictions"] == []


def test_manifest_cannot_self_certify_external_reviews(tmp_path):
    root = copy_fixture(tmp_path)

    manifest_path = root / "app" / "data" / "release-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["publicV1Status"] = "ready-for-public-release"

    write_json(manifest_path, manifest)

    report = GATE.evaluate(root)

    assert report["publicV1Status"] == "BLOCKED"
    assert report["contradictions"]
    assert GATE.policy_exit(report, "ci") == 2


def test_public_v1_claim_fails_ci_when_required_reviews_are_pending(tmp_path):
    root = copy_fixture(tmp_path)

    manifest_path = root / "app" / "data" / "release-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["release"] = "1.0.0"
    manifest["status"] = "public"

    write_json(manifest_path, manifest)

    report = GATE.evaluate(root)

    assert report["publicReleaseClaimDetected"] is True
    assert report["publicV1Status"] == "BLOCKED"
    assert GATE.policy_exit(report, "ci") == 2


def test_require_ready_fails_while_external_reviews_are_pending():
    report = GATE.evaluate(ROOT)

    assert GATE.policy_exit(report, "require-ready") == 1
    assert GATE.policy_exit(report, "expect-blocked") == 0


def test_valid_current_external_signoffs_satisfy_human_gates(tmp_path):
    root = copy_fixture(tmp_path)

    approve_clinical(root)
    approve_legal(root)

    report = GATE.evaluate(root)

    assert report["gates"]["external-clinical-review"]["satisfied"] is True
    assert report["gates"]["external-legal-review"]["satisfied"] is True
    assert report["publicV1Status"] == "READY"
    assert report["blockers"] == []


def test_changed_clinical_material_invalidates_approved_signoff(tmp_path):
    root = copy_fixture(tmp_path)

    approve_clinical(root)
    approve_legal(root)

    target = root / "app" / "data" / "polyvagal-theory.json"
    target.write_text(
        target.read_text(encoding="utf-8") + "\n ",
        encoding="utf-8",
    )

    report = GATE.evaluate(root)

    clinical_gate = report["gates"]["external-clinical-review"]

    assert clinical_gate["satisfied"] is False
    assert clinical_gate["snapshotIntegrity"]["status"] == "stale"
    assert "app/data/polyvagal-theory.json" in (clinical_gate["snapshotIntegrity"]["changedFiles"])
    assert "external-clinical-review" in report["blockers"]


def test_missing_snapshot_cannot_satisfy_external_review(tmp_path):
    root = copy_fixture(tmp_path)

    approve_clinical(root)
    approve_legal(root)

    path = root / "P3_1_EXTERNAL_CLINICAL_SIGNOFF.json"
    record = json.loads(path.read_text(encoding="utf-8"))
    record.pop("reviewSnapshot", None)
    write_json(path, record)

    report = GATE.evaluate(root)

    assert report["gates"]["external-clinical-review"]["satisfied"] is False
    assert report["gates"]["external-clinical-review"]["snapshotIntegrity"]["status"] == "missing"
