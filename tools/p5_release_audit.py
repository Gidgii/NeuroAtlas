from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "app"
OUT = ROOT / "P5_RELEASE_READINESS_REPORT.json"


def audit() -> dict:
    failures: list[str] = []
    required = [
        APP / "product-readiness.js",
        APP / "legal" / "privacy.html",
        APP / "legal" / "accessibility.html",
        APP / "legal" / "release.html",
    ]
    for path in required:
        if not path.is_file():
            failures.append(f"Missing release file: {path.relative_to(ROOT)}")

    manifest = json.loads((APP / "manifest.webmanifest").read_text(encoding="utf-8"))
    for field in ("name", "short_name", "id", "start_url", "display", "icons"):
        if not manifest.get(field):
            failures.append(f"Manifest missing field: {field}")

    sw = (APP / "sw.js").read_text(encoding="utf-8")
    for resource in (
        "./product-readiness.js",
        "./legal/privacy.html",
        "./legal/accessibility.html",
        "./legal/release.html",
    ):
        if resource not in sw:
            failures.append(f"Offline cache missing: {resource}")

    evidence = json.loads((APP / "data" / "evidence-library.json").read_text(encoding="utf-8"))
    review = json.loads((APP / "data" / "evidence-review-map.json").read_text(encoding="utf-8"))
    curriculum = json.loads((APP / "data" / "curriculum.json").read_text(encoding="utf-8"))

    concept_ids = {item["id"] for item in curriculum["concepts"]}
    mapped_ids = set(review.get("concepts", {}))
    if concept_ids - mapped_ids:
        failures.append(f"Evidence map missing {len(concept_ids - mapped_ids)} production concepts")

    report = {
        "phase": "P5",
        "status": "PASS" if not failures else "FAIL",
        "conceptCount": len(concept_ids),
        "evidenceSourceCount": len(evidence.get("sources", [])),
        "evidenceMappedConceptCount": len(concept_ids & mapped_ids),
        "privacyDocument": (APP / "legal" / "privacy.html").is_file(),
        "accessibilityDocument": (APP / "legal" / "accessibility.html").is_file(),
        "releaseGovernanceDocument": (APP / "legal" / "release.html").is_file(),
        "telemetryNetworkProviderEnabled": False,
        "accessibilityTarget": "WCAG 2.2 Level AA practices; no independent conformance claim",
        "failures": failures,
    }
    OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


def main() -> int:
    report = audit()
    print(f"P5 release-readiness audit: {report['status']}")
    print(
        f"Concepts: {report['conceptCount']} | evidence sources: "
        f"{report['evidenceSourceCount']} | mapped: {report['evidenceMappedConceptCount']}"
    )
    for failure in report["failures"]:
        print(f"FAIL: {failure}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
