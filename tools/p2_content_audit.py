#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).parents[1]
DATA = ROOT / "app" / "data"
REQUIRED_DEEP_DIVE = {"advancedClinicalDetail", "practicalExample", "limitationsCautions"}


def main() -> int:
    curriculum = json.loads((DATA / "curriculum.json").read_text(encoding="utf-8"))
    concepts = curriculum["concepts"]
    missing = []
    no_refs = []
    no_objectives = []
    structured = 0
    for concept in concepts:
        path = DATA / f"{concept['id']}.json"
        if not path.exists():
            missing.append(concept["id"])
            continue
        detail = json.loads(path.read_text(encoding="utf-8"))
        if not detail.get("references"):
            no_refs.append(concept["id"])
        if not detail.get("learningObjectives"):
            no_objectives.append(concept["id"])
        sections = detail.get("sections")
        if isinstance(sections, dict) and set(sections) >= REQUIRED_DEEP_DIVE:
            structured += 1
    report = {
        "registeredConcepts": len(concepts),
        "missingDetailRecords": missing,
        "conceptsWithoutReferences": no_refs,
        "conceptsWithoutLearningObjectives": no_objectives,
        "structuredDeepDiveReady": structured,
    }
    print(json.dumps(report, indent=2))
    return 1 if missing or no_refs or no_objectives else 0


if __name__ == "__main__":
    raise SystemExit(main())
