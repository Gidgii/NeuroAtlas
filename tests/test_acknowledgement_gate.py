from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "app"


def test_acknowledgement_gate_is_versioned_and_mandatory():
    js = (APP / "acknowledgement-gate.js").read_text(encoding="utf-8")

    assert "2026-08-21.1" in js
    assert "neuroatlas-acknowledgement" in js
    assert "acceptedAt" in js
    assert "local-device-only" in js
    assert "event.preventDefault()" in js

    for acknowledgement in (
        "educational-use",
        "independent-verification",
        "accuracy-limitations",
        "no-client-data",
    ):
        assert acknowledgement in js


def test_acknowledgement_gate_is_loaded_and_available_offline():
    index = (APP / "index.html").read_text(encoding="utf-8")
    sw = (APP / "sw.js").read_text(encoding="utf-8")

    assert 'href="acknowledgement-gate.css"' in index
    assert 'src="acknowledgement-gate.js"' in index

    for resource in (
        "./acknowledgement-gate.js",
        "./acknowledgement-gate.css",
        "./legal/disclaimer.html",
    ):
        assert resource in sw


def test_disclaimer_preserves_clinical_and_legal_boundaries():
    text = (APP / "legal" / "disclaimer.html").read_text(encoding="utf-8").lower()

    assert "not medical" in text
    assert "diagnostic or treatment advice" in text
    assert "independently verifying" in text
    assert "sole basis for a clinical decision" in text
    assert "errors, omissions" in text
    assert "patient/client" in text
    assert "australian consumer law" in text
    assert "cannot lawfully be excluded" in text
    assert "not a legal-clearance certificate" in text


def test_disclaimer_is_available_after_acceptance():
    product = (APP / "product-readiness.js").read_text(encoding="utf-8")

    assert "disclaimerDialog" in product
    assert "./legal/disclaimer.html" in product


def test_browser_qa_exercises_the_acknowledgement_gate():
    browser_qa = (ROOT / "tools" / "p8_browser_qa.py").read_text(encoding="utf-8")
    runtime_qa = (ROOT / "tools" / "runtime_qa.py").read_text(encoding="utf-8")

    assert "accept_acknowledgement_gate" in browser_qa
    assert "blockedBeforeComplete" in browser_qa
    assert "staleVersionReprompt" in browser_qa
    assert "disclaimerAccessibleAfterAcceptance" in browser_qa

    assert "_accept_acknowledgement_gate" in runtime_qa
    assert "Acknowledgement gate accepts the current notice" in runtime_qa
