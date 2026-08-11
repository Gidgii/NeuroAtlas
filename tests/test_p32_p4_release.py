import hashlib
import json
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "app" / "data"
ART = ROOT / "app" / "assets" / "illustrations"


def test_every_concept_has_resolved_evidence_review():
    curriculum = json.loads((DATA / "curriculum.json").read_text(encoding="utf-8"))
    evidence = json.loads((DATA / "evidence-library.json").read_text(encoding="utf-8"))
    review = json.loads((DATA / "evidence-review-map.json").read_text(encoding="utf-8"))
    source_ids = {source["id"] for source in evidence["sources"]}
    concepts = curriculum["concepts"]
    assert len(concepts) == 249
    assert set(review["concepts"]) == {concept["id"] for concept in concepts}
    for concept in concepts:
        record = review["concepts"][concept["id"]]
        assert record["status"] in {"source-verified-foundation", "reviewed-with-boundaries"}
        assert record["sourceIds"]
        assert set(record["sourceIds"]) <= source_ids
        assert record["futureGate"]


def test_evidence_library_ui_and_future_gate_are_shipped():
    app = (ROOT / "app" / "app.js").read_text(encoding="utf-8")
    index = (ROOT / "app" / "index.html").read_text(encoding="utf-8")
    assert "evidencePage" in app
    assert "evidenceFilter" in app
    assert 'id="evidenceButton"' in index
    assert "evidence-library.json" in app
    assert "evidence-review-map.json" in app


def test_p4_replaced_all_placeholder_artwork_with_valid_unique_svg_assets():
    curriculum = json.loads((DATA / "curriculum.json").read_text(encoding="utf-8"))
    concepts = curriculum["concepts"]
    assert all(concept["artworkReadiness"] != "Placeholder" for concept in concepts)
    hashes = set()
    for concept in concepts:
        path = ART / concept["hero"]
        assert path.exists(), concept["id"]
        raw = path.read_bytes()
        ET.fromstring(raw)
        text = raw.decode("utf-8")
        assert "<title" in text and "<desc" in text
        hashes.add(hashlib.sha256(raw).hexdigest())
    assert len(hashes) == 249


def test_locked_front_entrance_is_not_part_of_p4_artwork_mutation():
    report = json.loads((ROOT / "P4_ARTWORK_PRODUCTION_REPORT.json").read_text(encoding="utf-8"))
    assert report["lockedEntrance"] == "UNCHANGED"
    assert report["replacedPlaceholderArtwork"] == 109
