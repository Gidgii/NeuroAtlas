#!/usr/bin/env python3
"""Validate and safely import completed independent NeuroAtlas reviews."""

from __future__ import annotations

import argparse
import json
import shutil
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

try:
    from reviewer_snapshot import (
        SCOPES,
        has_review_activity,
        validate_snapshot,
    )
except ModuleNotFoundError:
    from tools.reviewer_snapshot import (
        SCOPES,
        has_review_activity,
        validate_snapshot,
    )

ROOT = Path(__file__).resolve().parents[1]

APPROVED_RECOMMENDATIONS = {
    "approve",
    "approved",
    "approve-with-minor-changes",
    "approved-with-minor-changes",
    "approve with minor changes",
    "approved with minor changes",
}

APPROVED_CONCEPT_DECISIONS = {
    "approve",
    "approved",
    "approve-with-minor-changes",
    "approved-with-minor-changes",
    "approve with minor changes",
    "approved with minor changes",
}

APPROVED_STATUSES = {
    "approved-external-review",
    "completed-external-review",
}

OBVIOUS_PLACEHOLDERS = {
    "test",
    "tester",
    "placeholder",
    "sample",
    "example",
    "independent reviewer",
    "independent lawyer",
    "n/a",
    "na",
    "none",
    "signed",
    "signature",
    "x",
    "yes",
}

IMMUTABLE_FIELDS = {
    "clinical": (
        "phase",
        "requiredSampleConceptCount",
        "sampleConceptIds",
        "boundary",
        "reviewSnapshot",
        "snapshotBoundary",
    ),
    "legal": (
        "phase",
        "releaseTarget",
        "boundary",
        "reviewSnapshot",
        "snapshotBoundary",
    ),
}

CLINICAL_GLOBAL_POSITIVE = (
    "evidenceWeightingAppropriate",
    "biomarkerLanguageAppropriate",
    "traumaClaimsNonDeterministic",
    "emdrEfficacyMechanismDistinctionAppropriate",
    "contestedTheoryBoundariesAppropriate",
    "diagnosticOverreachControlled",
)

LEGAL_SCOPE_FIELDS = (
    "disclaimerAndLimitationOfUse",
    "acknowledgementDesign",
    "copyrightAndAssetProvenance",
    "thirdPartyLicensing",
    "privacyPositionForCurrentLocalOnlyRelease",
)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def normalise(value: Any) -> str:
    return str(value or "").strip().lower()


def present(value: Any) -> bool:
    return value is not None and str(value).strip() != ""


def non_placeholder(value: Any) -> bool:
    return present(value) and normalise(value) not in OBVIOUS_PLACEHOLDERS


def valid_review_date(value: Any) -> bool:
    if not present(value):
        return False

    try:
        parsed = date.fromisoformat(str(value))
    except ValueError:
        return False

    return parsed <= datetime.now(UTC).date()


def add_issue(issues: list[str], message: str) -> None:
    if message not in issues:
        issues.append(message)


def validate_schema_boundary(
    current: dict[str, Any],
    returned: dict[str, Any],
    scope: str,
    issues: list[str],
) -> None:
    current_keys = set(current)
    returned_keys = set(returned)

    missing_keys = sorted(current_keys - returned_keys)
    extra_keys = sorted(returned_keys - current_keys)

    if missing_keys:
        add_issue(
            issues,
            "Returned sign-off is missing top-level fields: " + ", ".join(missing_keys),
        )

    if extra_keys:
        add_issue(
            issues,
            "Returned sign-off contains unexpected top-level fields: " + ", ".join(extra_keys),
        )

    for field in IMMUTABLE_FIELDS[scope]:
        if returned.get(field) != current.get(field):
            add_issue(
                issues,
                f"Frozen review field was altered: {field}",
            )


def validate_reviewer(
    reviewer: Any,
    scope: str,
    issues: list[str],
) -> None:
    if not isinstance(reviewer, dict):
        add_issue(issues, "independentReviewer must be an object.")
        return

    for field in ("name", "qualification"):
        if not non_placeholder(reviewer.get(field)):
            add_issue(
                issues,
                f"Reviewer {field} is missing or appears to be a placeholder.",
            )

    if scope == "clinical":
        if not non_placeholder(reviewer.get("registrationOrCredential")):
            add_issue(
                issues,
                "Clinical reviewer registrationOrCredential is required.",
            )

        expertise = reviewer.get("areasOfExpertise")
        if not isinstance(expertise, list) or not any(non_placeholder(item) for item in expertise):
            add_issue(
                issues,
                "Clinical reviewer must record at least one area of expertise.",
            )

    else:
        if not non_placeholder(reviewer.get("practisingCertificateOrCredential")):
            add_issue(
                issues,
                "Legal reviewer practisingCertificateOrCredential is required.",
            )

        if normalise(reviewer.get("jurisdiction")) != "australia":
            add_issue(
                issues,
                "Legal reviewer jurisdiction must be Australia for the current release review.",
            )


def decision_id(item: dict[str, Any]) -> str | None:
    value = item.get("conceptId")
    return str(value).strip() if present(value) else None


def validate_clinical(
    current: dict[str, Any],
    returned: dict[str, Any],
    issues: list[str],
) -> None:
    if normalise(returned.get("status")) not in APPROVED_STATUSES:
        add_issue(
            issues,
            "Clinical review status must indicate completed approval.",
        )

    validate_reviewer(
        returned.get("independentReviewer"),
        "clinical",
        issues,
    )

    if not valid_review_date(returned.get("reviewDate")):
        add_issue(
            issues,
            "Clinical reviewDate must be a valid non-future YYYY-MM-DD date.",
        )

    required_ids = list(current.get("sampleConceptIds", []))
    required_set = set(required_ids)

    required_count = current.get("requiredSampleConceptCount")

    if required_count != len(required_ids):
        add_issue(
            issues,
            "Current clinical sample count is internally inconsistent.",
        )

    if returned.get("reviewedConceptCount") != len(required_ids):
        add_issue(
            issues,
            "reviewedConceptCount must exactly match the required sample count.",
        )

    decisions = returned.get("conceptDecisions")

    if not isinstance(decisions, list):
        add_issue(issues, "conceptDecisions must be an array.")
        decisions = []

    if len(decisions) != len(required_ids):
        add_issue(
            issues,
            f"Exactly {len(required_ids)} clinical concept decisions are required.",
        )

    seen: list[str] = []

    for index, item in enumerate(decisions, start=1):
        if not isinstance(item, dict):
            add_issue(
                issues,
                f"Clinical decision {index} must be an object.",
            )
            continue

        allowed_keys = {
            "conceptId",
            "decision",
            "comments",
            "requestedChanges",
        }

        unexpected = sorted(set(item) - allowed_keys)

        if unexpected:
            add_issue(
                issues,
                f"Clinical decision {index} contains unexpected fields: " + ", ".join(unexpected),
            )

        concept_id = decision_id(item)

        if concept_id is None:
            add_issue(
                issues,
                f"Clinical decision {index} is missing conceptId.",
            )
            continue

        seen.append(concept_id)

        if concept_id not in required_set:
            add_issue(
                issues,
                f"Unexpected clinical concept decision: {concept_id}",
            )

        decision = normalise(item.get("decision"))

        if decision not in APPROVED_CONCEPT_DECISIONS:
            add_issue(
                issues,
                f"Concept {concept_id} is not release-approved: {item.get('decision')}",
            )

        if "minor changes" in decision or "minor-changes" in decision:
            comments = item.get("comments")
            changes = item.get("requestedChanges")

            has_comments = present(comments)
            has_changes = (
                present(changes)
                if not isinstance(changes, list)
                else any(present(change) for change in changes)
            )

            if not has_comments and not has_changes:
                add_issue(
                    issues,
                    f"Concept {concept_id} is approved with minor changes "
                    "but no requested change was recorded.",
                )

    if len(seen) != len(set(seen)):
        add_issue(
            issues,
            "Duplicate clinical concept decisions were returned.",
        )

    if set(seen) != required_set:
        missing = sorted(required_set - set(seen))

        if missing:
            add_issue(
                issues,
                "Missing clinical concept decisions: " + ", ".join(missing),
            )

    findings = returned.get("globalFindings")

    if not isinstance(findings, dict):
        add_issue(issues, "globalFindings must be an object.")
    else:
        current_findings = current.get("globalFindings", {})

        if set(findings) != set(current_findings):
            add_issue(
                issues,
                "Clinical globalFindings schema was altered.",
            )

        for field in CLINICAL_GLOBAL_POSITIVE:
            if findings.get(field) is not True:
                add_issue(
                    issues,
                    f"Clinical global finding must be true: {field}",
                )

        if findings.get("materialClinicalSafetyConcerns") is not False:
            add_issue(
                issues,
                "Material clinical safety concerns must be resolved "
                "before release approval can be imported.",
            )

    if normalise(returned.get("finalRecommendation")) not in APPROVED_RECOMMENDATIONS:
        add_issue(
            issues,
            "Clinical finalRecommendation is not an approved release outcome.",
        )

    if not non_placeholder(returned.get("signatureOrElectronicAcknowledgement")):
        add_issue(
            issues,
            "Clinical reviewer signature/electronic acknowledgement "
            "is missing or appears to be a placeholder.",
        )

    if returned.get("gateSatisfied") is not True:
        add_issue(
            issues,
            "Clinical gateSatisfied must be explicitly true in the completed reviewer return.",
        )


def validate_legal(
    current: dict[str, Any],
    returned: dict[str, Any],
    issues: list[str],
) -> None:
    if normalise(returned.get("status")) not in APPROVED_STATUSES:
        add_issue(
            issues,
            "Legal review status must indicate completed approval.",
        )

    validate_reviewer(
        returned.get("independentReviewer"),
        "legal",
        issues,
    )

    if not valid_review_date(returned.get("reviewDate")):
        add_issue(
            issues,
            "Legal reviewDate must be a valid non-future YYYY-MM-DD date.",
        )

    scope_record = returned.get("scope")

    if not isinstance(scope_record, dict):
        add_issue(issues, "Legal scope must be an object.")
    else:
        current_scope = current.get("scope", {})

        if set(scope_record) != set(current_scope):
            add_issue(
                issues,
                "Legal review scope schema was altered.",
            )

        for field in LEGAL_SCOPE_FIELDS:
            if scope_record.get(field) is not True:
                add_issue(
                    issues,
                    f"Legal review scope item is incomplete: {field}",
                )

    findings = returned.get("findings")

    if not isinstance(findings, dict):
        add_issue(issues, "Legal findings must be an object.")
    else:
        current_findings = current.get("findings", {})

        if set(findings) != set(current_findings):
            add_issue(
                issues,
                "Legal findings schema was altered.",
            )

        if findings.get("materialLegalConcerns") is not False:
            add_issue(
                issues,
                "Material legal concerns must be resolved before release approval can be imported.",
            )

        required_changes = findings.get("requiredChanges")

        if not isinstance(required_changes, list):
            add_issue(
                issues,
                "Legal findings.requiredChanges must remain an array.",
            )

    recommendation = normalise(returned.get("finalRecommendation"))

    if recommendation not in APPROVED_RECOMMENDATIONS:
        add_issue(
            issues,
            "Legal finalRecommendation is not an approved release outcome.",
        )

    if recommendation in {"approve", "approved"}:
        changes = findings.get("requiredChanges", []) if isinstance(findings, dict) else []

        if isinstance(changes, list) and any(present(change) for change in changes):
            add_issue(
                issues,
                "Legal review says APPROVE but still records required changes.",
            )

    if not non_placeholder(returned.get("signatureOrElectronicAcknowledgement")):
        add_issue(
            issues,
            "Legal reviewer signature/electronic acknowledgement "
            "is missing or appears to be a placeholder.",
        )

    if returned.get("gateSatisfied") is not True:
        add_issue(
            issues,
            "Legal gateSatisfied must be explicitly true in the completed reviewer return.",
        )


def validate_returned(
    root: Path,
    scope: str,
    returned_path: Path,
) -> dict[str, Any]:
    issues: list[str] = []

    signoff_path = root / str(SCOPES[scope]["signoff"])

    try:
        current = load_json(signoff_path)
    except (OSError, json.JSONDecodeError) as exc:
        return {
            "valid": False,
            "scope": scope,
            "issues": [f"Current sign-off could not be loaded: {exc}"],
        }

    try:
        returned = load_json(returned_path)
    except (OSError, json.JSONDecodeError) as exc:
        return {
            "valid": False,
            "scope": scope,
            "issues": [f"Returned sign-off could not be loaded: {exc}"],
        }

    validate_schema_boundary(
        current,
        returned,
        scope,
        issues,
    )

    current_snapshot = current.get("reviewSnapshot")
    returned_snapshot = returned.get("reviewSnapshot")

    if returned_snapshot != current_snapshot:
        add_issue(
            issues,
            "Returned reviewSnapshot does not exactly match the current frozen reviewer snapshot.",
        )

    snapshot_result = validate_snapshot(
        root,
        returned_snapshot,
        scope,
    )

    if snapshot_result.get("valid") is not True:
        add_issue(
            issues,
            f"Reviewed source snapshot is no longer current: {snapshot_result.get('status')}",
        )

    if scope == "clinical":
        validate_clinical(
            current,
            returned,
            issues,
        )
    else:
        validate_legal(
            current,
            returned,
            issues,
        )

    return {
        "valid": not issues,
        "scope": scope,
        "returnedFile": str(returned_path),
        "targetSignoff": str(SCOPES[scope]["signoff"]),
        "snapshotIntegrity": snapshot_result,
        "manualIndependenceConfirmationRequired": True,
        "independenceMachineVerifiable": False,
        "issues": issues,
    }


def evaluate_release(root: Path) -> dict[str, Any]:
    try:
        from public_v1_gate import evaluate
    except ModuleNotFoundError:
        from tools.public_v1_gate import evaluate

    return evaluate(root)


def apply_returned(
    root: Path,
    scope: str,
    returned_path: Path,
    validation: dict[str, Any],
    confirm_independent: bool,
) -> dict[str, Any]:
    if validation.get("valid") is not True:
        raise RuntimeError("Refusing to import an invalid returned review.")

    if not confirm_independent:
        raise RuntimeError(
            "Import requires explicit operator confirmation that the reviewer "
            "is genuinely independent and appropriately qualified."
        )

    target = root / str(SCOPES[scope]["signoff"])
    current = load_json(target)

    if has_review_activity(current, scope):
        raise RuntimeError(
            "Current production sign-off already contains reviewer activity. "
            "Refusing to overwrite an existing human review."
        )

    backup_dir = root / "external-review-import-backups"
    backup_dir.mkdir(parents=True, exist_ok=True)

    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    backup = backup_dir / f"{scope}-signoff-before-import-{stamp}.json"

    shutil.copy2(target, backup)

    returned = load_json(returned_path)

    target.write_text(
        json.dumps(
            returned,
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    snapshot_result = validate_snapshot(
        root,
        returned.get("reviewSnapshot"),
        scope,
    )

    if snapshot_result.get("valid") is not True:
        shutil.copy2(backup, target)
        raise RuntimeError(
            "Imported review invalidated snapshot integrity. Production sign-off was rolled back."
        )

    release_report = evaluate_release(root)

    gate_id = "external-clinical-review" if scope == "clinical" else "external-legal-review"

    gate = release_report.get("gates", {}).get(gate_id, {})

    if gate.get("satisfied") is not True:
        shutil.copy2(backup, target)
        raise RuntimeError(
            "Imported review did not satisfy the machine release gate. "
            "Production sign-off was rolled back."
        )

    return {
        "applied": True,
        "scope": scope,
        "target": str(target),
        "backup": str(backup),
        "gateSatisfiedAfterImport": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--scope",
        choices=("clinical", "legal"),
        required=True,
    )
    parser.add_argument(
        "--input",
        required=True,
    )
    parser.add_argument(
        "--apply",
        action="store_true",
    )
    parser.add_argument(
        "--confirm-independent-reviewer",
        action="store_true",
    )
    parser.add_argument(
        "--write-report",
    )

    args = parser.parse_args()

    returned_path = Path(args.input)

    if not returned_path.is_absolute():
        returned_path = ROOT / returned_path

    validation = validate_returned(
        ROOT,
        args.scope,
        returned_path,
    )

    result: dict[str, Any] = {
        "validation": validation,
        "import": None,
    }

    exit_code = 0 if validation["valid"] else 1

    if args.apply:
        try:
            result["import"] = apply_returned(
                ROOT,
                args.scope,
                returned_path,
                validation,
                args.confirm_independent_reviewer,
            )
        except RuntimeError as exc:
            result["import"] = {
                "applied": False,
                "error": str(exc),
            }
            exit_code = 2

    if args.write_report:
        report_path = Path(args.write_report)

        if not report_path.is_absolute():
            report_path = ROOT / report_path

        report_path.write_text(
            json.dumps(
                result,
                indent=2,
                ensure_ascii=False,
            )
            + "\n",
            encoding="utf-8",
        )

    print(
        json.dumps(
            result,
            indent=2,
            ensure_ascii=False,
        )
    )

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
