import json
from pathlib import Path

ROOT = Path(__file__).parents[1]
DATA_DIR = ROOT / "app" / "data"


def test_integrated_case_labs_have_complete_reasoning_contracts():
    records = []
    for path in DATA_DIR.glob("*.json"):
        payload = json.loads(path.read_text(encoding="utf-8"))
        lab = payload.get("integratedCaseLab")
        if lab:
            records.append((path, lab))

    assert len(records) >= 3
    case_count = 0
    for path, lab in records:
        cases = lab.get("cases") or []
        assert cases, f"{path.name}: integratedCaseLab has no cases"
        for case in cases:
            case_count += 1
            for field in (
                "id",
                "label",
                "vignette",
                "targetHypothesis",
                "hypothesisRationale",
                "targetAssessment",
                "assessmentRationale",
                "synthesis",
                "caveat",
            ):
                assert case.get(field), f"{path.name}: {case.get('id')} missing {field}"
            assert case["targetHypothesis"] in case.get("hypothesisOptions", [])
            assert case["targetAssessment"] in case.get("assessmentOptions", [])
            assert len(case.get("hypothesisOptions", [])) >= 2
            assert len(case.get("assessmentOptions", [])) >= 2
            assert case.get("supports")
            assert case.get("challenges")
            assert case.get("alternatives")

    assert case_count >= 6
