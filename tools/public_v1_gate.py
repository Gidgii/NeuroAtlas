#!/usr/bin/env python3
"""Machine-enforced public-v1 release governance for NeuroAtlas.

The gate derives release readiness from evidence records. It does not permit
the release manifest itself to self-certify required independent reviews.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

try:
    from reviewer_snapshot import validate_snapshot
except ModuleNotFoundError:
    from tools.reviewer_snapshot import validate_snapshot

ROOT = Path(__file__).resolve().parents[1]

APPROVED_RECOMMENDATIONS = {
    "approve",
    "approved",
    "approve-with-minor-changes",
    "approved-with-minor-changes",
    "approve with minor changes",
    "approved with minor changes",
}

PUBLIC_RELEASE_STATUSES = {
    "public",
    "released",
    "production",
    "stable",
    "general-availability",
    "general availability",
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def present(value: Any) -> bool:
    return value is not None and str(value).strip() != ""


def normalise(value: Any) -> str:
    return str(value or "").strip().lower()


def decision_id(record: dict[str, Any]) -> str | None:
    for key in ("conceptId", "concept_id", "id"):
        value = record.get(key)
        if present(value):
            return str(value)
    return None


def evaluate(root: Path = ROOT) -> dict[str, Any]:
    manifest = load_json(root / "app" / "data" / "release-manifest.json")
    acknowledgement = load_json(root / "P8_ACKNOWLEDGEMENT_GATE_REPORT.json")
    evidence = load_json(root / "P3_2_EVIDENCE_GOVERNANCE_REPORT.json")
    clinical = load_json(root / "P3_1_EXTERNAL_CLINICAL_SIGNOFF.json")
    legal_internal = load_json(root / "P8_LEGAL_LICENSING_GOVERNANCE_REPORT.json")
    legal_external = load_json(root / "P8_EXTERNAL_LEGAL_SIGNOFF.json")
    runtime = load_json(root / "RUNTIME_QA_REPORT.json")

    clinical_snapshot = validate_snapshot(
        root,
        clinical.get("reviewSnapshot"),
        "clinical",
    )
    legal_snapshot = validate_snapshot(
        root,
        legal_external.get("reviewSnapshot"),
        "legal",
    )

    acknowledgement_ok = (
        acknowledgement.get("status") == "PASS"
        and acknowledgement.get("noticeVersion") == "2026-08-21.1"
        and acknowledgement.get("acceptanceRecord", {}).get("versioned") is True
        and acknowledgement.get("acceptanceRecord", {}).get("staleNoticeRequiresReacceptance")
        is True
    )

    evidence_ok = (
        normalise(evidence.get("status")).startswith("complete")
        and evidence.get("productionConcepts") == evidence.get("evidenceMappedConcepts")
        and int(evidence.get("productionConcepts", 0)) > 0
    )

    runtime_summary = runtime.get("summary", {})
    runtime_ok = (
        int(runtime_summary.get("failed", 1)) == 0
        and int(runtime_summary.get("passed", 0)) > 0
        and not runtime.get("console_errors")
        and not runtime.get("page_errors")
        and not runtime.get("request_failures")
    )

    reviewer = clinical.get("independentReviewer", {})
    required_sample = set(clinical.get("sampleConceptIds", []))
    decisions = clinical.get("conceptDecisions", [])
    reviewed_ids = {
        concept_id
        for item in decisions
        if isinstance(item, dict)
        for concept_id in [decision_id(item)]
        if concept_id
    }

    global_findings = clinical.get("globalFindings", {})
    required_global_findings = (
        "evidenceWeightingAppropriate",
        "biomarkerLanguageAppropriate",
        "traumaClaimsNonDeterministic",
        "emdrEfficacyMechanismDistinctionAppropriate",
        "contestedTheoryBoundariesAppropriate",
        "diagnosticOverreachControlled",
        "materialClinicalSafetyConcerns",
    )

    clinical_global_complete = all(
        global_findings.get(key) is not None for key in required_global_findings
    )

    clinical_ok = (
        clinical.get("gateSatisfied") is True
        and clinical_snapshot.get("valid") is True
        and present(reviewer.get("name"))
        and present(reviewer.get("qualification"))
        and present(clinical.get("reviewDate"))
        and int(clinical.get("reviewedConceptCount", 0))
        >= int(clinical.get("requiredSampleConceptCount", 25))
        and required_sample
        and required_sample.issubset(reviewed_ids)
        and clinical_global_complete
        and global_findings.get("materialClinicalSafetyConcerns") is False
        and normalise(clinical.get("finalRecommendation")) in APPROVED_RECOMMENDATIONS
        and present(clinical.get("signatureOrElectronicAcknowledgement"))
    )

    internal_boundary = legal_internal.get("releaseBoundary", {})
    legal_findings = legal_internal.get("findings", {})

    legal_inventory_ok = (
        internal_boundary.get("internalInventoryCompleted") is True
        and legal_findings.get("dependencyLicencesResolved") is True
        and legal_findings.get("projectRootCopyrightNoticeAdded") is True
    )

    legal_reviewer = legal_external.get("independentReviewer", {})
    legal_scope = legal_external.get("scope", {})
    legal_external_findings = legal_external.get("findings", {})

    required_legal_scope = (
        "disclaimerAndLimitationOfUse",
        "acknowledgementDesign",
        "copyrightAndAssetProvenance",
        "thirdPartyLicensing",
        "privacyPositionForCurrentLocalOnlyRelease",
    )

    legal_external_ok = (
        legal_external.get("gateSatisfied") is True
        and legal_snapshot.get("valid") is True
        and present(legal_reviewer.get("name"))
        and present(legal_reviewer.get("qualification"))
        and present(legal_external.get("reviewDate"))
        and all(legal_scope.get(key) is True for key in required_legal_scope)
        and legal_external_findings.get("materialLegalConcerns") is False
        and normalise(legal_external.get("finalRecommendation")) in APPROVED_RECOMMENDATIONS
        and present(legal_external.get("signatureOrElectronicAcknowledgement"))
    )

    legal_ok = legal_inventory_ok and legal_external_ok

    gates = {
        "evidence-governance": {
            "required": True,
            "satisfied": evidence_ok,
            "evidence": "P3_2_EVIDENCE_GOVERNANCE_REPORT.json",
        },
        "acknowledgement-gate": {
            "required": True,
            "satisfied": acknowledgement_ok,
            "evidence": "P8_ACKNOWLEDGEMENT_GATE_REPORT.json",
        },
        "runtime-regression": {
            "required": True,
            "satisfied": runtime_ok,
            "evidence": "RUNTIME_QA_REPORT.json",
        },
        "external-clinical-review": {
            "required": True,
            "satisfied": clinical_ok,
            "evidence": "P3_1_EXTERNAL_CLINICAL_SIGNOFF.json",
            "snapshotIntegrity": clinical_snapshot,
        },
        "external-legal-review": {
            "required": True,
            "satisfied": legal_ok,
            "evidence": "P8_EXTERNAL_LEGAL_SIGNOFF.json",
            "snapshotIntegrity": legal_snapshot,
        },
        "external-accessibility-review": {
            "required": False,
            "recommended": True,
            "satisfied": False,
            "evidence": None,
        },
    }

    blockers = [
        gate_id
        for gate_id, gate in gates.items()
        if gate.get("required") and not gate.get("satisfied")
    ]

    status = "READY" if not blockers else "BLOCKED"

    manifest_release = normalise(manifest.get("release"))
    manifest_status = normalise(manifest.get("status"))
    declared_v1_status = normalise(manifest.get("publicV1Status"))

    public_claim = (
        manifest_release in {"1.0.0", "v1.0.0"} or manifest_status in PUBLIC_RELEASE_STATUSES
    )

    declared_ready = declared_v1_status in {
        "ready",
        "ready-for-public-release",
        "public-v1-ready",
    }

    contradictions: list[str] = []

    if public_claim and blockers:
        contradictions.append(
            "Release manifest claims a public/stable v1 release while required "
            "governance gates remain unsatisfied."
        )

    if declared_ready and blockers:
        contradictions.append(
            "release-manifest.json declares public v1 ready while derived "
            "evidence still contains blockers."
        )

    return {
        "schemaVersion": "1.0",
        "release": manifest.get("release"),
        "manifestStatus": manifest.get("status"),
        "publicV1Status": status,
        "publicReleaseClaimDetected": public_claim,
        "gates": gates,
        "blockers": blockers,
        "contradictions": contradictions,
        "safeForCandidateDevelopment": not contradictions,
    }


def policy_exit(report: dict[str, Any], mode: str) -> int:
    if report["contradictions"]:
        return 2

    if mode == "require-ready":
        return 0 if report["publicV1Status"] == "READY" else 1

    if mode == "expect-blocked":
        return 0 if report["publicV1Status"] == "BLOCKED" else 1

    # CI policy:
    # Candidate development may continue while genuine external reviews remain
    # pending. A public/stable v1 claim can only exist when every required gate
    # is satisfied.
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--ci", action="store_true")
    modes.add_argument("--require-ready", action="store_true")
    modes.add_argument("--expect-blocked", action="store_true")
    parser.add_argument("--write-report")
    args = parser.parse_args()

    report = evaluate()

    if args.write_report:
        path = Path(args.write_report)
        if not path.is_absolute():
            path = ROOT / path
        path.write_text(
            json.dumps(report, indent=2) + "\n",
            encoding="utf-8",
        )

    print(json.dumps(report, indent=2))

    mode = "ci"
    if args.require_ready:
        mode = "require-ready"
    elif args.expect_blocked:
        mode = "expect-blocked"

    return policy_exit(report, mode)


if __name__ == "__main__":
    raise SystemExit(main())
