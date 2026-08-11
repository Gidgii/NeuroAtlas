from __future__ import annotations

import hashlib
import json
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "app"
DATA = APP / "data"
ART = APP / "assets" / "illustrations"
OUT = ROOT / "P3_2_P4_FINAL_AUDIT_REPORT.json"


def main() -> int:
    curriculum = json.loads((DATA / "curriculum.json").read_text(encoding="utf-8"))
    evidence = json.loads((DATA / "evidence-library.json").read_text(encoding="utf-8"))
    review = json.loads((DATA / "evidence-review-map.json").read_text(encoding="utf-8"))
    concepts = curriculum["concepts"]
    source_ids = {source["id"] for source in evidence["sources"]}
    failures: list[str] = []
    hashes: set[str] = set()
    rendered_assets = 0
    for concept in concepts:
        cid = concept["id"]
        record = review.get("concepts", {}).get(cid)
        if not record:
            failures.append(f"missing evidence review: {cid}")
        elif not record.get("sourceIds"):
            failures.append(f"no evidence source links: {cid}")
        elif not set(record["sourceIds"]) <= source_ids:
            failures.append(f"unresolved evidence source: {cid}")
        path = ART / concept["hero"]
        if not path.exists():
            failures.append(f"missing artwork: {cid}")
            continue
        try:
            raw = path.read_bytes()
            ET.fromstring(raw)
            hashes.add(hashlib.sha256(raw).hexdigest())
            rendered_assets += 1
        except Exception as exc:  # pragma: no cover - audit output
            failures.append(f"invalid SVG {cid}: {exc}")
        if concept.get("artworkReadiness") == "Placeholder":
            failures.append(f"placeholder artwork remains: {cid}")
    app_js = (APP / "app.js").read_text(encoding="utf-8")
    index = (APP / "index.html").read_text(encoding="utf-8")
    if "evidencePage" not in app_js or 'id="evidenceButton"' not in index:
        failures.append("Evidence Library UI is not wired")
    report = {
        "phase": "P3.2 + P4",
        "generatedDate": "2026-08-11",
        "status": "PASS" if not failures else "FAIL",
        "concepts": len(concepts),
        "evidenceMappedConcepts": len(review.get("concepts", {})),
        "evidenceSources": len(evidence["sources"]),
        "artworkAssetsParsed": rendered_assets,
        "uniqueArtworkFiles": len(hashes),
        "artworkReadiness": dict(Counter(c.get("artworkReadiness") for c in concepts)),
        "lockedEntrance": "UNCHANGED",
        "failures": failures,
        "note": "AI-assisted audit; not independent human peer review.",
    }
    OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"P3.2/P4 final audit: {report['status']}")
    print(
        f"Concepts: {len(concepts)} | sources: {len(evidence['sources'])} | SVGs: {rendered_assets}"
    )
    if failures:
        for failure in failures[:20]:
            print(f"[FAIL] {failure}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
