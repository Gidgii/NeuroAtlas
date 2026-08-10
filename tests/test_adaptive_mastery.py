from pathlib import Path

ROOT = Path(__file__).parents[1]


def test_adaptive_mastery_module_and_app_contracts():
    module = (ROOT / "app" / "mastery-tracker.js").read_text(encoding="utf-8")
    app = (ROOT / "app" / "app.js").read_text(encoding="utf-8")

    assert "export class MasteryTracker" in module
    assert "recordQuiz(id,correct)" in module
    assert "recordReview(id,grade)" in module
    assert "weakest(ids" in module
    assert "rankCards(cards" in module
    assert "new MasteryTracker()" in app
    assert "state.mastery.recordQuiz" in app
    assert "state.mastery.recordReview" in app
    assert "Retrieval priorities" in app
    assert "data-focus-review" in app
    assert "reviewPrompts" in app
