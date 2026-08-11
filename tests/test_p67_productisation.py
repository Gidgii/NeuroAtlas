import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "app"
DATA = APP / "data"


def test_p67_assessment_bank_is_evidence_linked_and_registered():
    bank = json.loads((DATA / "assessment-bank.json").read_text(encoding="utf-8"))
    evidence = json.loads((DATA / "evidence-library.json").read_text(encoding="utf-8"))
    curriculum = json.loads((DATA / "curriculum.json").read_text(encoding="utf-8"))
    evidence_ids = {source["id"] for source in evidence["sources"]}
    concept_ids = {concept["id"] for concept in curriculum["concepts"]}

    assert len(bank["cases"]) >= 18
    assert len({case["domain"] for case in bank["cases"]}) >= 7
    for case in bank["cases"]:
        assert case["prompt"]
        assert len(case["choices"]) >= 4
        assert 0 <= case["correctIndex"] < len(case["choices"])
        assert case["rationale"]
        assert case["competency"] in {"recognise", "explain", "localise", "compare", "apply"}
        assert case["conceptIds"]
        assert set(case["conceptIds"]) <= concept_ids
        assert case["evidenceIds"]
        assert set(case["evidenceIds"]) <= evidence_ids


def test_p67_assessment_engine_contains_adaptive_confidence_and_remediation_paths():
    source = (APP / "p67-learning.js").read_text(encoding="utf-8")
    for token in (
        "adaptiveCase",
        "assessment-confidence",
        "highConfidenceErrors",
        "data-remediate",
        "evidenceIds",
        "window.openAtlasConcept",
    ):
        assert token in source


def test_p67_educator_tools_are_local_and_exportable():
    source = (APP / "p67-learning.js").read_text(encoding="utf-8")
    assert "PATHWAYS" in source
    assert "Export JSON" in source
    assert "Export CSV" in source
    assert "window.print" in source
    assert "cna-assigned-pathway-v1" in source
    assert "navigator.sendBeacon" not in source
    assert "XMLHttpRequest" not in source


def test_p67_index_and_service_worker_include_productisation_assets():
    index = (APP / "index.html").read_text(encoding="utf-8")
    sw = (APP / "sw.js").read_text(encoding="utf-8")
    for resource in ("p67-learning.js", "p67-learning.css"):
        assert resource in index
        assert f"./{resource}" in sw
    assert "./data/assessment-bank.json" not in sw  # runtime-cached after first successful fetch


def test_p67_assessment_rationales_keep_diagnostic_guardrails():
    bank = json.loads((DATA / "assessment-bank.json").read_text(encoding="utf-8"))
    by_id = {case["id"]: case for case in bank["cases"]}
    assert "as a stand-alone ADHD diagnostic test" in by_id["eeg-03"]["rationale"]
    assert "no meaningful group-level benefit" in by_id["nf-01"]["rationale"]
    assert "as established standard care" in by_id["nf-02"]["rationale"]
    assert (
        "Treatment efficacy and mechanism are distinct questions"
        in by_id["trauma-01"]["rationale"]
    )


def test_p67_does_not_modify_locked_entrance_asset_contract():
    report = json.loads((ROOT / "P3_2_P4_FINAL_AUDIT_REPORT.json").read_text(encoding="utf-8"))
    assert report["lockedEntrance"] == "UNCHANGED"
