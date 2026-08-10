from pathlib import Path

ROOT = Path(__file__).parents[1]


def test_progressive_competency_tracker_and_ui_contracts():
    tracker = (ROOT / "app" / "competency-tracker.js").read_text(encoding="utf-8")
    app = (ROOT / "app" / "app.js").read_text(encoding="utf-8")

    for skill in ("recognise", "explain", "localise", "compare", "apply"):
        assert f"id:'{skill}'" in tracker
    assert "export class CompetencyTracker" in tracker
    assert "nextSkill(id,available" in tracker
    assert "aggregate(skill,ids)" in tracker
    assert "new CompetencyTracker()" in app
    assert "availableCompetencies(c)" in app
    assert "competencyPrompt(c,skill)" in app
    assert "state.competency.record(c.id,'recognise'" in app
    assert "state.competency.record(card.id,state.reviewSkill" in app
    assert "Competency profile" in app
    assert "Current target:" in app


def test_competency_capabilities_are_grounded_in_existing_labs():
    app = (ROOT / "app" / "app.js").read_text(encoding="utf-8")
    assert "d.spatialMap||d.pathwayTrace" in app
    assert "d.clinicalComparison||d.lesionLab" in app
    assert "d.assessmentLab||d.integratedCaseLab" in app
