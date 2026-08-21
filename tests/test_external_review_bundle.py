from __future__ import annotations

import json
import zipfile
from pathlib import Path

import pytest

from tools import build_external_review_bundle as BUNDLE

ROOT = Path(__file__).parents[1]


@pytest.mark.parametrize("scope", ("clinical", "legal"))
def test_external_review_bundle_is_valid_and_deterministic(
    tmp_path: Path,
    scope: str,
):
    report = BUNDLE.build_and_verify(
        ROOT,
        scope,
        tmp_path,
    )

    assert report["valid"] is True
    assert report["deterministic"] is True
    assert report["manifestValid"] is True
    assert report["missingFiles"] == []
    assert report["unexpectedFiles"] == []
    assert report["hashFailures"] == []


@pytest.mark.parametrize("scope", ("clinical", "legal"))
def test_bundle_contains_snapshot_and_signoff(
    tmp_path: Path,
    scope: str,
):
    bundle_path = BUNDLE.build_bundle(
        ROOT,
        scope,
        tmp_path,
    )

    signoff_path = str(BUNDLE.SCOPES[scope]["signoff"])
    signoff = BUNDLE.load_json(ROOT / signoff_path)
    snapshot = signoff["reviewSnapshot"]

    with zipfile.ZipFile(bundle_path, "r") as archive:
        names = set(archive.namelist())

        assert signoff_path in names
        assert "00_READ_ME_FIRST.txt" in names
        assert "00_BUNDLE_MANIFEST.json" in names

        for item in snapshot["files"]:
            assert item["path"] in names

        manifest = json.loads(archive.read("00_BUNDLE_MANIFEST.json").decode("utf-8"))

    assert manifest["snapshotDigest"] == snapshot["digest"]
    assert manifest["reviewSignoff"] == signoff_path


def test_bundle_builder_refuses_stale_snapshot(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    stale = {
        "valid": False,
        "status": "stale",
    }

    monkeypatch.setattr(
        BUNDLE,
        "validate_snapshot",
        lambda *_args, **_kwargs: stale,
    )

    with pytest.raises(RuntimeError, match="Refusing to package"):
        BUNDLE.build_bundle(
            ROOT,
            "clinical",
            tmp_path,
        )
