from __future__ import annotations

import json
import shutil
from pathlib import Path

from tools import reviewer_snapshot as SNAPSHOT

ROOT = Path(__file__).parents[1]


def copy_scope(tmp_path: Path, scope: str) -> Path:
    for relative in SNAPSHOT.scope_paths(ROOT, scope):
        source = ROOT / relative
        target = tmp_path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    return tmp_path


def test_current_pending_signoffs_have_current_snapshots():
    for scope in ("clinical", "legal"):
        signoff_path = ROOT / str(SNAPSHOT.SCOPES[scope]["signoff"])
        signoff = json.loads(signoff_path.read_text(encoding="utf-8"))

        result = SNAPSHOT.validate_snapshot(
            ROOT,
            signoff.get("reviewSnapshot"),
            scope,
        )

        assert result["valid"] is True
        assert result["status"] == "valid"
        assert result["changedFiles"] == []
        assert result["missingFiles"] == []
        assert result["unexpectedFiles"] == []


def test_snapshot_digest_is_deterministic():
    first = SNAPSHOT.create_snapshot(ROOT, "clinical")
    second = SNAPSHOT.create_snapshot(ROOT, "clinical")

    assert first["digest"] == second["digest"]
    assert first["files"] == second["files"]


def test_changed_reviewed_file_invalidates_snapshot(tmp_path):
    root = copy_scope(tmp_path, "clinical")
    snapshot = SNAPSHOT.create_snapshot(root, "clinical")

    target = root / "app" / "data" / "polyvagal-theory.json"
    target.write_text(
        target.read_text(encoding="utf-8") + "\n ",
        encoding="utf-8",
    )

    result = SNAPSHOT.validate_snapshot(root, snapshot, "clinical")

    assert result["valid"] is False
    assert result["status"] == "stale"
    assert "app/data/polyvagal-theory.json" in result["changedFiles"]


def test_snapshot_digest_tampering_is_rejected():
    snapshot = SNAPSHOT.create_snapshot(ROOT, "legal")
    snapshot["digest"] = "0" * 64

    result = SNAPSHOT.validate_snapshot(ROOT, snapshot, "legal")

    assert result["valid"] is False
    assert result["status"] == "invalid"
    assert result["aggregateDigestValid"] is False
