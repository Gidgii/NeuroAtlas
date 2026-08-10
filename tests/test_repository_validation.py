import json
import re
from pathlib import Path

ROOT = Path(__file__).parents[1]
APP = ROOT / "app"
DATA = APP / "data"
ILLUSTRATIONS = APP / "assets" / "illustrations"
STATE = json.loads((ROOT / "PROJECT_STATE.json").read_text(encoding="utf-8"))
CURRICULUM = json.loads((DATA / "curriculum.json").read_text(encoding="utf-8"))
ARTWORK_REPORT = json.loads((ROOT / "ARTWORK_READINESS_REPORT.json").read_text(encoding="utf-8"))
ATLAS_IDS = STATE["interactiveAnatomy"]["verifiedStructures"]
ARTWORK_STATUSES = {
    "Placeholder",
    "Functional",
    "Ready for Production",
    "Premium",
    "Locked",
}


def detail(structure_id):
    return json.loads((DATA / f"{structure_id}.json").read_text(encoding="utf-8"))


def registered_loader_ids():
    source = (APP / "app.js").read_text(encoding="utf-8")
    block = re.search(r"const detailFiles=\[(.*?)\];const detailResponses", source, re.S)
    assert block
    return set(re.findall(r"'([^']+)'", block.group(1)))


def service_worker_paths():
    source = (APP / "sw.js").read_text(encoding="utf-8")
    block = re.search(r"const CORE=(\[.*?\]);\s*self\.addEventListener", source, re.S)
    assert block
    return json.loads(block.group(1))


def test_all_json_files_parse():
    for path in ROOT.rglob("*.json"):
        json.loads(path.read_text(encoding="utf-8"))


def test_curriculum_ids_and_level_orders_are_unique():
    ids = [concept["id"] for concept in CURRICULUM["concepts"]]
    positions = [(concept["level"], concept["order"]) for concept in CURRICULUM["concepts"]]
    assert len(ids) == len(set(ids))
    assert len(positions) == len(set(positions))


def test_production_details_are_filename_aligned_and_registered():
    loader_ids = registered_loader_ids()
    for path in DATA.glob("*.json"):
        if path.name == "curriculum.json":
            continue
        record = json.loads(path.read_text(encoding="utf-8"))
        if record.get("status") != "production":
            continue
        assert record["id"] == path.stem
        assert record["id"] in loader_ids


def test_loader_requests_only_registered_production_concept_details():
    curriculum_ids = {concept["id"] for concept in CURRICULUM["concepts"]}
    expected_loader_ids = set()
    for concept_id in curriculum_ids:
        path = DATA / f"{concept_id}.json"
        if not path.is_file():
            continue
        record = json.loads(path.read_text(encoding="utf-8"))
        if record.get("status") == "production":
            expected_loader_ids.add(concept_id)
    assert registered_loader_ids() == expected_loader_ids


def test_curriculum_illustrations_exist():
    for concept in CURRICULUM["concepts"]:
        assert (ILLUSTRATIONS / concept["hero"]).is_file()


def test_every_concept_has_valid_artwork_readiness():
    concepts = CURRICULUM["concepts"]
    statuses = [concept["artworkReadiness"] for concept in concepts]
    assert set(CURRICULUM["artworkReadinessScale"]) == ARTWORK_STATUSES
    assert all(status in ARTWORK_STATUSES for status in statuses)
    assert len({concept["hero"] for concept in concepts}) == len(concepts)
    assert ARTWORK_REPORT["totalConcepts"] == len(concepts)
    assert ARTWORK_REPORT["totalIllustrations"] == len(concepts)
    assert ARTWORK_REPORT["counts"] == {
        status: statuses.count(status) for status in ARTWORK_STATUSES
    }


def test_service_worker_has_unique_complete_production_coverage():
    paths = service_worker_paths()
    assert len(paths) == len(set(paths))
    cached = set(paths)
    expected_data_paths = {"./data/curriculum.json"}
    for path in DATA.glob("*.json"):
        if path.name == "curriculum.json":
            continue
        record = json.loads(path.read_text(encoding="utf-8"))
        if record.get("status") == "production":
            expected_data_paths.add(f"./data/{path.name}")
    assert {path for path in cached if path.startswith("./data/")} == expected_data_paths
    for concept in CURRICULUM["concepts"]:
        assert f"./assets/illustrations/{concept['hero']}" in cached


def test_quizzes_have_valid_answers_and_rationales():
    for path in DATA.glob("*.json"):
        if path.name == "curriculum.json":
            continue
        record = json.loads(path.read_text(encoding="utf-8"))
        questions = record.get("quizBank") or record.get("quiz") or []
        for question in questions:
            answer = question.get("answer", question.get("correctAnswer"))
            assert answer is not None
            assert 0 <= answer < len(question["options"])
            assert question.get("rationale") or question.get("explanation")


def test_interactive_anatomy_navigation_is_bidirectional():
    records = {structure_id: detail(structure_id) for structure_id in ATLAS_IDS}
    for structure_id, record in records.items():
        previous_id = record.get("previousConcept")
        next_id = record.get("nextConcept")
        if previous_id in records:
            assert records[previous_id].get("nextConcept") == structure_id
        if next_id in records:
            assert records[next_id].get("previousConcept") == structure_id


def test_all_registered_structures_use_canonical_explorer_schema():
    assert len(ATLAS_IDS) == STATE["interactiveAnatomy"]["structuresCompleted"]
    for structure_id in ATLAS_IDS:
        record = detail(structure_id)
        explorer = record["explorer"]
        assert explorer["schemaVersion"] == "1.0.0"
        assert explorer["partsSource"] == "anatomy"
        assert explorer["stages"] == ["inputs", "connections", "outputs"]
        assert set(explorer["overlays"]) == {"bloodSupply", "functions", "lesions", "symptoms"}
        assert explorer["returnToOverview"] is True
        assert explorer["accessibility"] == {
            "keyboard": True,
            "screenReader": True,
            "reducedMotion": True,
            "touchTargetPx": 44,
        }


def test_generic_explorer_has_safe_empty_and_optional_stage_guards():
    source = (APP / "system-explorer.js").read_text(encoding="utf-8")
    assert "if(!first)return" in source
    assert "if(!run||!stages.length)return" in source
    assert "if(!stage){finish();return}" in source
    assert "prefers-reduced-motion: reduce" in source
    assert 'aria-live="polite"' in source


def test_runtime_does_not_expose_unsupported_visual_controls_or_empty_explorers():
    app_source = (APP / "app.js").read_text(encoding="utf-8")
    visual_source = (APP / "visual-scenes.js").read_text(encoding="utf-8")
    explorer_source = (APP / "system-explorer.js").read_text(encoding="utf-8")
    assert "hasVisualScene(c.id)" in app_source
    assert "visualAvailable&&state.visualOpen" in app_source
    assert "state.visualOpen=!state.visualOpen" in app_source
    assert "export const hasVisualScene" in visual_source
    assert "if(!first)return ''" in explorer_source
    assert "No selectable anatomy is available for this record." not in explorer_source


def test_concept_hero_uses_content_specific_accessible_text_when_available():
    source = (APP / "app.js").read_text(encoding="utf-8")
    assert "d?.altText||d?.accessibility?.altText" in source
    assert 'alt="${escapeHTML(conceptAlt(c))}"' in source


def test_build_35_comparison_is_complete_and_optional_runtime_is_safe():
    record = detail("healthy-versus-pathology-comparison")
    assert record["previousConcept"] == "brain-lateralisation-comparison"
    assert record["nextConcept"] == "lesion-and-symptom-mapping"
    assert len(record["quiz"]) >= 3
    assert record["searchTerms"]
    assert record["spacedRepetition"]["reviewPrompt"]
    assert record["accessibility"]["reducedMotion"] is True
    assert record["explorer"]["comparisonModes"] == [
        {"id": "healthy", "label": "Healthy variation", "part": "variation"},
        {"id": "pathology", "label": "Pathology patterns", "part": "structural"},
    ]
    source = (APP / "system-explorer.js").read_text(encoding="utf-8")
    assert "details.explorer?.comparisonModes" in source
    assert "'Healthy and pathology comparison'" in source
    assert "data-system-comparison" in source


def test_build_36_lesion_mapping_is_complete_and_optional_runtime_is_safe():
    record = detail("lesion-and-symptom-mapping")
    assert record["previousConcept"] == "healthy-versus-pathology-comparison"
    assert record["nextConcept"] == "integrated-whole-brain-explorer-and-capstone"
    assert len(record["quiz"]) >= 3
    assert all(question.get("rationale") for question in record["quiz"])
    assert record["searchTerms"]
    assert record["spacedRepetition"]["reviewPrompt"]
    assert record["accessibility"]["reducedMotion"] is True
    assert record["explorer"]["comparisonModes"] == [
        {"id": "left", "label": "Left hemisphere", "part": "left-cortical"},
        {"id": "right", "label": "Right hemisphere", "part": "right-cortical"},
    ]
    assert record["explorer"]["comparisonLabel"] == "Left and right lesion comparison"
    assert {part["id"] for part in record["explorerParts"]} >= {
        "left-cortical",
        "right-cortical",
        "subcortical",
        "white-matter",
        "brainstem",
        "cerebellar",
        "distributed",
    }
    source = (APP / "system-explorer.js").read_text(encoding="utf-8")
    assert "details.explorer?.comparisonLabel" in source


def test_build_37_capstone_navigates_every_completed_anatomy_structure():
    record = detail("integrated-whole-brain-explorer-and-capstone")
    assert record["previousConcept"] == "lesion-and-symptom-mapping"
    assert record["nextConcept"] is None
    assert len(record["quiz"]) >= 3
    assert all(question.get("rationale") for question in record["quiz"])
    assert record["searchTerms"]
    assert record["spacedRepetition"]["reviewPrompt"]
    assert record["accessibility"]["reducedMotion"] is True
    destinations = {
        destination
        for part in record["explorerParts"]
        for destination in [
            *part.get("conceptIds", []),
            *([part["conceptId"]] if part.get("conceptId") else []),
        ]
    }
    prior_atlas_ids = set(ATLAS_IDS) - {record["id"]}
    assert destinations == prior_atlas_ids
    assert {mode["id"] for mode in record["explorer"]["comparisonModes"]} == {
        "left",
        "right",
        "healthy",
        "pathology",
    }
    source = (APP / "system-explorer.js").read_text(encoding="utf-8")
    assert "data-open=" in source
    assert "system-destinations" in source
    assert "bindDestinations" in source
    assert "openAtlasConcept" in (APP / "app.js").read_text(encoding="utf-8")
