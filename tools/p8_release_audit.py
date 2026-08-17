#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).parents[1]
APP = ROOT / "app"


def audit():
    errors = []
    required = [
        APP / "p8-release.js",
        APP / "p8-release.css",
        APP / "data/release-manifest.json",
        APP / "legal/third-party-notices.html",
        ROOT / "P8_RELEASE_CANDIDATE_REPORT.json",
    ]
    errors += [f"Missing: {p.relative_to(ROOT)}" for p in required if not p.exists()]
    manifest = json.loads((APP / "data/release-manifest.json").read_text(encoding="utf-8"))
    if manifest.get("release") != "1.0.0-rc1":
        errors.append("Unexpected RC version")
    if manifest.get("featureFreeze") is not True:
        errors.append("Feature freeze not declared")
    index = (APP / "index.html").read_text(encoding="utf-8")
    for token in ("p8-release.css", "p8-release.js"):
        if token not in index:
            errors.append(f"index.html missing {token}")
    sw = (APP / "sw.js").read_text(encoding="utf-8")
    for token in ("p8-release.css", "p8-release.js", "third-party-notices.html"):
        if token not in sw:
            errors.append(f"service worker missing {token}")

    for token in ("release-manifest.json", "assessment-bank.json"):
        if token in sw:
            errors.append(f"service worker must not precache {token}")
    readiness = (APP / "product-readiness.js").read_text(encoding="utf-8")
    if "phase: 'P8'" not in readiness:
        errors.append("Product readiness phase is not P8")
    release = (APP / "legal/release.html").read_text(encoding="utf-8").lower()
    if "not a claim of independent" not in release:
        errors.append("Release caveat missing")
    licensing = (APP / "legal/third-party-notices.html").read_text(encoding="utf-8").lower()
    if "not a legal clearance certificate" not in licensing:
        errors.append("Licensing caveat missing")
    return {
        "status": "PASS" if not errors else "FAIL",
        "release": "1.0.0-rc1",
        "featureFreeze": True,
        "errors": errors,
    }


def main():
    report = audit()
    print(json.dumps(report, indent=2))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
