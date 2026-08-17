import json
from pathlib import Path

ROOT = Path(__file__).parents[1]
APP = ROOT / "app"


def test_release_manifest_declares_rc_and_feature_freeze():
    data = json.loads((APP / "data/release-manifest.json").read_text(encoding="utf-8"))
    assert data["release"] == "1.0.0-rc1"
    assert data["status"] == "release-candidate"
    assert data["featureFreeze"] is True
    assert "github-ci" in data["releaseGates"]


def test_p8_assets_use_the_correct_cache_strategy():
    index = (APP / "index.html").read_text(encoding="utf-8")
    sw = (APP / "sw.js").read_text(encoding="utf-8")

    # P8 shell assets and the static legal notice belong in the precache.
    for token in ("p8-release.css", "p8-release.js"):
        assert token in index
        assert token in sw
    assert "third-party-notices.html" in sw

    # Dynamic JSON preserves the P6/P7 runtime-cache contract.
    for token in ("release-manifest.json", "assessment-bank.json"):
        assert token not in sw

    # Both dynamic JSON resources remain packaged with the application.
    assert (APP / "data" / "release-manifest.json").is_file()
    assert (APP / "data" / "assessment-bank.json").is_file()


def test_release_position_does_not_claim_external_certification():
    release = (APP / "legal/release.html").read_text(encoding="utf-8").lower()
    notices = (APP / "legal/third-party-notices.html").read_text(encoding="utf-8").lower()
    assert "not a claim of independent" in release
    assert "not a legal clearance certificate" in notices


def test_beta_feedback_is_local_export_not_network_submission():
    js = (APP / "p8-release.js").read_text(encoding="utf-8")
    assert "Export a local feedback file" in js
    assert "downloadJson(" in js
    assert "fetch(" not in js
    assert "XMLHttpRequest" not in js


def test_product_readiness_is_p8():
    js = (APP / "product-readiness.js").read_text(encoding="utf-8")
    assert "phase: 'P8'" in js
    assert "Release candidate hardening" in js
