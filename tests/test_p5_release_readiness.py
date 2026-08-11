import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "app"


def test_p5_release_documents_exist_and_are_linkable():
    index = (APP / "index.html").read_text(encoding="utf-8")
    product = (APP / "product-readiness.js").read_text(encoding="utf-8")
    assert "product-readiness.js" in index
    for name in ("privacy.html", "accessibility.html", "release.html"):
        path = APP / "legal" / name
        assert path.is_file()
        assert f"./legal/{name}" in product


def test_p5_manifest_is_installability_ready():
    manifest = json.loads((APP / "manifest.webmanifest").read_text(encoding="utf-8"))
    assert manifest["name"]
    assert manifest["short_name"]
    assert manifest["id"]
    assert manifest["start_url"]
    assert manifest["display"] in {"standalone", "fullscreen", "minimal-ui"}
    assert manifest.get("prefer_related_applications") is False
    sizes = {icon["sizes"] for icon in manifest["icons"]}
    assert {"192x192", "512x512"} <= sizes


def test_p5_service_worker_caches_release_files():
    sw = (APP / "sw.js").read_text(encoding="utf-8")
    for resource in (
        "./product-readiness.js",
        "./legal/privacy.html",
        "./legal/accessibility.html",
        "./legal/release.html",
    ):
        assert resource in sw


def test_p5_search_scope_and_telemetry_are_local_only():
    product = (APP / "product-readiness.js").read_text(encoding="utf-8")
    assert "searchScope" in product
    assert "CustomEvent" in product
    assert "fetch(" in product  # static local metadata fetch only
    assert "navigator.sendBeacon" not in product
    assert "XMLHttpRequest" not in product
    assert "analytics.google" not in product


def test_p5_accessibility_statement_does_not_overclaim_conformance():
    page = (APP / "legal" / "accessibility.html").read_text(encoding="utf-8")
    assert "WCAG 2.2 Level AA" in page
    assert "not independently certified" in page
    assert "Automated tests cannot establish full WCAG conformance" in page
