import json
from pathlib import Path

ROOT = Path(__file__).parents[1]
DATA = ROOT / "app" / "data"
FOUNDATIONS = {
    "cell",
    "membrane",
    "electricity",
    "chemistry",
    "brain-overview",
    "lobes",
    "subcortex",
    "brainstem-cerebellum",
}


def test_every_registered_concept_has_detail_references_and_objectives():
    curriculum = json.loads((DATA / "curriculum.json").read_text(encoding="utf-8"))
    for concept in curriculum["concepts"]:
        path = DATA / f"{concept['id']}.json"
        assert path.exists(), f"Missing detail record: {concept['id']}"
        detail = json.loads(path.read_text(encoding="utf-8"))
        assert detail.get("learningObjectives"), f"No objectives: {concept['id']}"
        assert detail.get("references"), f"No references: {concept['id']}"


def test_foundation_gap_records_support_secondary_clinical_depth():
    for concept_id in FOUNDATIONS:
        detail = json.loads((DATA / f"{concept_id}.json").read_text(encoding="utf-8"))
        sections = detail.get("sections") or {}
        for key in ("advancedClinicalDetail", "practicalExample", "limitationsCautions"):
            assert sections.get(key), f"{concept_id}: missing {key}"
        assert len(detail["learningObjectives"]) >= 3
        assert len(detail["references"]) >= 2


def test_deep_dive_ui_is_optional_and_accessible():
    app = (ROOT / "app" / "app.js").read_text(encoding="utf-8")
    module = (ROOT / "app" / "deep-dive.js").read_text(encoding="utf-8")
    assert "renderDeepDiveButton" in app
    assert "bindDeepDive" in app
    assert "data-open-deep-dive" in module
    assert "showModal()" in module
    assert 'aria-label="Close deep dive"' in module
