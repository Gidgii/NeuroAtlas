import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "app" / "data"
OUT = ROOT / "P6_P7_PRODUCTISATION_REPORT.json"


def main():
    bank = json.loads((DATA / "assessment-bank.json").read_text(encoding="utf-8"))
    evidence = json.loads((DATA / "evidence-library.json").read_text(encoding="utf-8"))
    curriculum = json.loads((DATA / "curriculum.json").read_text(encoding="utf-8"))
    evidence_ids = {source["id"] for source in evidence["sources"]}
    concept_ids = {concept["id"] for concept in curriculum["concepts"]}
    failures = []

    for case in bank["cases"]:
        missing_evidence = sorted(set(case["evidenceIds"]) - evidence_ids)
        missing_concepts = sorted(set(case["conceptIds"]) - concept_ids)
        if missing_evidence:
            failures.append(f"{case['id']}: missing evidence {missing_evidence}")
        if missing_concepts:
            failures.append(f"{case['id']}: missing concepts {missing_concepts}")
        if not case.get("rationale"):
            failures.append(f"{case['id']}: missing rationale")

    report = {
        "phase": "P6-P7",
        "status": "PASS" if not failures else "FAIL",
        "assessmentCases": len(bank["cases"]),
        "domains": sorted({case["domain"] for case in bank["cases"]}),
        "competencies": sorted({case["competency"] for case in bank["cases"]}),
        "evidenceLinks": sum(len(case["evidenceIds"]) for case in bank["cases"]),
        "conceptRemediationLinks": sum(len(case["conceptIds"]) for case in bank["cases"]),
        "indexedEvidenceSources": len(evidence["sources"]),
        "productionConcepts": len(curriculum["concepts"]),
        "privacyBoundary": (
            "Assessment and educator records remain local unless the user exports them."
        ),
        "clinicalBoundary": (
            "Assessment items teach evidence-weighted reasoning and do not replace clinical "
            "diagnosis, "
            "supervision, credentialing, or patient-specific assessment."
        ),
        "lockedEntrance": "UNCHANGED",
        "failures": failures,
    }
    OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"P6/P7 productisation audit: {report['status']}")
    print(
        f"Cases: {report['assessmentCases']} | domains: {len(report['domains'])} "
        f"| evidence links: {report['evidenceLinks']}"
    )
    if failures:
        for failure in failures:
            print(f"[FAIL] {failure}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
