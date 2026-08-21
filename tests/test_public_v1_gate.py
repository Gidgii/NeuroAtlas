from __future__ import annotations

import importlib.util
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).parents[1]

SPEC = importlib.util.spec_from_file_location(
    "public_v1_gate",
    ROOT / "tools" / "public_v1_gate.py",
)
assert SPEC and SPEC.loader
GATE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(GATE)

GOVERNANCE_FILES = (
    "P8_ACKNOWLEDGEMENT_GATE_REPORT.json",
    "P3_2_EVIDENCE_GOVERNANCE_REPORT.json",
    "P3_1_EXTERNAL_CLINICAL_SIGNOFF.json",
    "P8_LEGAL_LICENSING_GOVERNANCE_REPORT.json",
    "P8_EXTERNAL_LEGAL_SIGNOFF.json",
    "RUNTIME_QA_REPORT.json",
)


def copy_fixture(tmp_path: Path) -> Path:
    (tmp_path / "app" / "data").mkdir(parents=True)

    shutil.copy2(
        ROOT / "app" / "data" / "release-manifest.json",
        tmp_path / "app" / "data" / "release-manifest.json",
    )

    for relative in GOVERNANCE_FILES:
        shutil.copy2(ROOT / relative, tmp_path / relative)

    return tmp_path


def test_current_release_candidate_is_truthfully_blocked():
    report = GATE.evaluate(ROOT)

    assert report["publicV1Status"] == "BLOCKED"
    assert "external-clinical-review" in report["blockers"]
    assert "external-legal-review" in report["blockers"]
    assert report["gates"]["acknowledgement-gate"]["satisfied"] is True
    assert report["gates"]["evidence-governance"]["satisfied"] is True
    assert report["gates"]["runtime-regression"]["satisfied"] is True
    assert report["contradictions"] == []


def test_manifest_cannot_self_certify_external_reviews(tmp_path):
    root = copy_fixture(tmp_path)

    manifest_path = root / "app" / "data" / "release-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["publicV1Status"] = "ready-for-public-release"

    manifest_path.write_text(
        json.dumps(manifest, indent=2) + "\n",
        encoding="utf-8",
    )

    report = GATE.evaluate(root)

    assert report["publicV1Status"] == "BLOCKED"
    assert report["contradictions"]
    assert GATE.policy_exit(report, "ci") == 2


def test_public_v1_claim_fails_ci_when_required_reviews_are_pending(tmp_path):
    root = copy_fixture(tmp_path)

    manifest_path = root / "app" / "data" / "release-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["release"] = "1.0.0"
    manifest["status"] = "public"

    manifest_path.write_text(
        json.dumps(manifest, indent=2) + "\n",
        encoding="utf-8",
    )

    report = GATE.evaluate(root)

    assert report["publicReleaseClaimDetected"] is True
    assert report["publicV1Status"] == "BLOCKED"
    assert GATE.policy_exit(report, "ci") == 2


def test_require_ready_fails_while_external_reviews_are_pending():
    report = GATE.evaluate(ROOT)

    assert GATE.policy_exit(report, "require-ready") == 1
    assert GATE.policy_exit(report, "expect-blocked") == 0
