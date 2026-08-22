from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).parents[1]


def load_json(relative: str):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def curriculum_ids() -> set[str]:
    curriculum = load_json("app/data/curriculum.json")
    return {item["id"] for item in curriculum["concepts"]}


def test_experience_architecture_is_explicitly_locked():
    lock = load_json("EXPERIENCE_ARCHITECTURE_LOCK.json")

    assert lock["status"] == "LOCKED-FOR-ARTWORK"
    assert lock["entryFlow"] == [
        "acknowledgement-if-required",
        "splash",
        "mode-gateway",
        "selected-experience",
    ]
    assert lock["crossModeBridge"]["bidirectional"] is True
    assert lock["crossModeBridge"]["supportsNoDirectLocalisation"] is True
    assert lock["artworkBoundary"]["finalArtworkDeferred"] is True


def test_index_exposes_locked_entry_and_two_modes():
    html = (ROOT / "app/index.html").read_text(encoding="utf-8")

    assert 'id="experienceRoot"' in html
    assert 'id="app" class="app-shell" hidden' in html
    assert 'data-route="brain"' in html
    assert ">Theory</button>" in html
    assert ">Brain</button>" in html
    assert 'src="experience-shell.js"' in html
    assert 'href="experience-shell.css"' in html


def test_experience_shell_enforces_splash_then_mode_gateway():
    source = (ROOT / "app/experience-shell.js").read_text(encoding="utf-8")

    assert 'data-experience-stage="splash"' in source
    assert "data-enter-atlas" in source
    assert 'data-experience-stage="gateway"' in source
    assert 'data-experience-mode="theory"' in source
    assert 'data-experience-mode="brain"' in source
    assert "NeuroAtlasAcknowledgement?.accepted" in source


def test_interactive_brain_registers_exactly_25_existing_targets():
    bridge = load_json("app/data/brain-bridge.json")
    ids = curriculum_ids()

    targets = bridge["interactiveTargets"]
    target_ids = [item["id"] for item in targets]

    assert len(target_ids) == 25
    assert len(set(target_ids)) == 25
    assert set(target_ids).issubset(ids)


def test_theory_brain_links_are_valid_and_bounded():
    bridge = load_json("app/data/brain-bridge.json")
    ids = curriculum_ids()
    target_ids = {item["id"] for item in bridge["interactiveTargets"]}
    allowed_kinds = set(bridge["relationKinds"])

    for source, links in bridge["links"].items():
        assert source in ids
        assert source not in bridge["noDirectLocalisation"]
        assert links

        seen_targets: set[str] = set()

        for link in links:
            assert link["target"] in target_ids
            assert link["target"] not in seen_targets
            seen_targets.add(link["target"])

            assert link["kind"] in allowed_kinds
            assert link["label"].strip()
            assert link["rationale"].strip()
            assert link["boundary"].strip()


def test_no_direct_localisation_boundaries_reference_real_concepts():
    bridge = load_json("app/data/brain-bridge.json")
    ids = curriculum_ids()

    boundaries = bridge["noDirectLocalisation"]

    assert set(boundaries).issubset(ids)

    for concept_id, reason in boundaries.items():
        assert concept_id not in bridge["links"]
        assert len(reason.strip()) >= 40

    assert "polyvagal-theory" in boundaries
    assert "structural-dissociation" in boundaries
    assert "window-of-tolerance" in boundaries
    assert "current-evidence-emdr" in boundaries
    assert "qeeg-adhd-evidence" in boundaries


def test_high_value_theory_to_brain_links_exist():
    bridge = load_json("app/data/brain-bridge.json")

    fear_targets = {item["target"] for item in bridge["links"]["fear-extinction-trauma"]}

    assert "limbic-system-atlas" in fear_targets
    assert "cingulate-cortex-atlas" in fear_targets
    assert "cerebral-lobes-atlas" in fear_targets

    salience_targets = {item["target"] for item in bridge["links"]["salience-network-trauma"]}

    assert "functional-network-overlay-atlas" in salience_targets
    assert "insula-atlas" in salience_targets


def test_review_scopes_include_new_clinical_and_legal_behaviour():
    clinical = (ROOT / "P3_1_EXTERNAL_CLINICAL_REVIEW_PACK.md").read_text(encoding="utf-8")

    legal = (ROOT / "P8_EXTERNAL_LEGAL_REVIEW_PACK.md").read_text(encoding="utf-8")

    assert "- File: `app/data/brain-bridge.json`" in clinical
    assert "- File: `app/experience-shell.js`" in legal
    assert "- File: `app/experience-shell.css`" in legal


def test_service_worker_caches_locked_experience_files():
    sw = (ROOT / "app/sw.js").read_text(encoding="utf-8")

    assert "./experience-shell.js" in sw
    assert "./experience-shell.css" in sw
    assert "./data/brain-bridge.json" in sw
