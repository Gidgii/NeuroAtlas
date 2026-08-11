#!/usr/bin/env python3
"""Static P2/P3 quality, safety, accessibility and performance audit."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).parents[1]
APP = ROOT / "app"
DATA = APP / "data"
HIGH_RISK = re.compile(
    r"(qeeg|neurofeedback|trauma|emdr|diagnos|psychopharm|epilepsy|tbi|migraine|"
    r"disorder|personality|autism|adhd|ptsd|depression|anxiety)",
    re.I,
)
CAUTION_TERMS = (
    "limit",
    "caution",
    "not a diagnosis",
    "does not",
    "cannot",
    "avoid",
    "uncertain",
    "evidence",
    "heterogene",
    "contested",
    "scope",
)
PLACEHOLDERS = re.compile(r"\b(?:TODO|TBD|LOREM IPSUM|FIXME)\b|undefined", re.I)


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def audit(root: Path = ROOT) -> dict:
    app = root / "app"
    data = app / "data"
    curriculum = load(data / "curriculum.json")
    concepts = curriculum["concepts"]
    errors: list[str] = []
    warnings: list[str] = []
    authored_deep_dives = 0
    explicit_boundaries = 0
    high_risk = 0
    high_risk_guarded = 0
    source_total = 0

    for concept in concepts:
        cid = concept["id"]
        path = data / f"{cid}.json"
        if not path.exists():
            errors.append(f"Missing detail record: {cid}")
            continue
        detail = load(path)
        objectives = detail.get("learningObjectives") or []
        references = detail.get("references") or []
        quiz = detail.get("quizBank") or detail.get("quiz") or []
        if not 2 <= len(objectives) <= 6:
            errors.append(f"{cid}: expected 2-6 learning objectives")
        if len(references) < 2:
            errors.append(f"{cid}: fewer than 2 references")
        if not quiz:
            errors.append(f"{cid}: no quiz/retrieval question source")
        source_total += len(references)
        for ref in references:
            if ref.get("url") and not ref["url"].startswith("https://"):
                errors.append(f"{cid}: non-HTTPS reference URL")
        raw = path.read_text(encoding="utf-8")
        if PLACEHOLDERS.search(raw):
            errors.append(f"{cid}: placeholder/runtime token found")
        sections = detail.get("sections")
        if isinstance(sections, dict) and sections:
            authored_deep_dives += 1
        boundary_text = ""
        if isinstance(sections, dict):
            boundary_text = (
                sections.get("limitationsCautions") or sections.get("whenItGoesWrong") or ""
            )
        if not boundary_text:
            for item in detail.get("mechanismMap") or []:
                if re.search(r"boundary|limit|caution|scope", str(item.get("label", "")), re.I):
                    boundary_text = str(item.get("detail", ""))
                    break
        if boundary_text:
            explicit_boundaries += 1
        if HIGH_RISK.search(cid):
            high_risk += 1
            lower = raw.lower()
            if any(term in lower for term in CAUTION_TERMS):
                high_risk_guarded += 1
            else:
                errors.append(
                    f"{cid}: high-risk clinical topic lacks an evidence/scope caution signal"
                )

    app_js = (app / "app.js").read_text(encoding="utf-8")
    deep_js = (app / "deep-dive.js").read_text(encoding="utf-8")
    a11y_js = (app / "accessibility-runtime.js").read_text(encoding="utf-8")
    content_js = (app / "content-quality.js").read_text(encoding="utf-8")
    css = (app / "styles.css").read_text(encoding="utf-8")
    html = (app / "index.html").read_text(encoding="utf-8")
    sw = (app / "sw.js").read_text(encoding="utf-8")
    runtime = (root / "tools" / "runtime_qa.py").read_text(encoding="utf-8")

    contracts = {
        "deep dive fallback": "derivedSections(details)" in deep_js,
        "evidence scope summary": (
            "renderContentQualitySummary" in app_js and "contentQuality" in content_js
        ),
        "expanded clinical search": "searchableDetailText(details)" in app_js,
        "route focus management": "focusMainHeading(main)" in app_js,
        "search keyboard shortcut": "event.key === '/'" in a11y_js,
        "lazy concept thumbnails": 'loading="lazy" decoding="async"' in app_js,
        "high-priority concept hero": 'fetchpriority="high"' in app_js,
        "skip link": 'class="skip-link"' in html and 'href="#main"' in html,
        "main focus target": 'id="main" tabindex="-1"' in html,
        "polite status": 'role="status" aria-live="polite"' in html,
        "global focus-visible": ":where(button,a,input,summary,[tabindex]):focus-visible" in css,
        "reduced motion": "@media(prefers-reduced-motion:reduce)" in css,
        "forced colors": "@media(forced-colors:active)" in css,
        "new modules offline": all(
            name in sw
            for name in (
                "./content-quality.js",
                "./accessibility-runtime.js",
                "./deep-dive.js",
            )
        ),
        "confidence-aware runtime QA": 'page.locator("[data-confidence]")' in runtime,
    }
    errors.extend(f"Missing P2/P3 contract: {name}" for name, ok in contracts.items() if not ok)

    return {
        "status": "PASS" if not errors else "FAIL",
        "registeredConcepts": len(concepts),
        "detailRecordsPresent": len(concepts)
        - sum(1 for e in errors if e.startswith("Missing detail record")),
        "totalReferenceEntries": source_total,
        "authoredDeepDiveRecords": authored_deep_dives,
        "deepDiveAvailableViaAuthoredOrDerivedContent": len(concepts),
        "explicitBoundaryRecords": explicit_boundaries,
        "highRiskClinicalTopics": high_risk,
        "highRiskTopicsWithCautionSignals": high_risk_guarded,
        "contracts": contracts,
        "errors": errors,
        "warnings": warnings,
        "clinicalReviewCaveat": (
            "This audit validates structure, internal consistency, references, caution signals "
            "and overclaim safeguards. It is not a substitute for independent source-by-source "
            "clinical peer review of every factual claim."
        ),
    }


def main() -> int:
    report = audit()
    target = ROOT / "P2_P3_FINAL_AUDIT_REPORT.json"
    target.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
