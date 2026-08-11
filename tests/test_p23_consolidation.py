import importlib.util
from pathlib import Path

ROOT = Path(__file__).parents[1]


def _audit_module():
    path = ROOT / "tools" / "p23_final_audit.py"
    spec = importlib.util.spec_from_file_location("p23_final_audit", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(module)
    return module


def test_p2_p3_final_audit_passes():
    report = _audit_module().audit(ROOT)
    assert report["status"] == "PASS", report["errors"]
    assert report["registeredConcepts"] == 249
    assert report["detailRecordsPresent"] == 249
    assert report["deepDiveAvailableViaAuthoredOrDerivedContent"] == 249
    assert report["highRiskClinicalTopics"] == report["highRiskTopicsWithCautionSignals"]


def test_p3_accessibility_and_performance_contracts_are_present():
    report = _audit_module().audit(ROOT)
    contracts = report["contracts"]
    assert contracts["route focus management"]
    assert contracts["search keyboard shortcut"]
    assert contracts["lazy concept thumbnails"]
    assert contracts["reduced motion"]
    assert contracts["forced colors"]
    assert contracts["new modules offline"]
