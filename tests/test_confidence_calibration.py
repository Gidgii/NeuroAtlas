from pathlib import Path

ROOT = Path(__file__).parents[1]


def test_confidence_calibration_tracker_contract():
    tracker = (ROOT / "app" / "calibration-tracker.js").read_text(encoding="utf-8")
    assert "export const CONFIDENCE_LEVELS" in tracker
    assert "export class CalibrationTracker" in tracker
    assert "highConfidenceErrors" in tracker
    assert "lowConfidenceSuccess" in tracker
    assert "profile()" in tracker
    assert "guidance(profile=this.profile())" in tracker


def test_review_and_progress_use_calibration_layer():
    app = (ROOT / "app" / "app.js").read_text(encoding="utf-8")
    assert "new CalibrationTracker()" in app
    assert "data-confidence" in app
    assert "state.reviewConfidence" in app
    assert "state.calibration.record" in app
    assert "Confidence calibration" in app
    assert "Does confidence match performance?" in app
