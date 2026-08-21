#!/usr/bin/env python3
"""Create and validate immutable reviewer-content snapshots for NeuroAtlas."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

SCHEMA_VERSION = "1.0"
ALGORITHM = "sha256-text-lf-v1"

SCOPES = {
    "clinical": {
        "scopeId": "external-clinical-review",
        "pack": "P3_1_EXTERNAL_CLINICAL_REVIEW_PACK.md",
        "signoff": "P3_1_EXTERNAL_CLINICAL_SIGNOFF.json",
        "supplemental": ("app/data/evidence-library.json",),
    },
    "legal": {
        "scopeId": "external-legal-review",
        "pack": "P8_EXTERNAL_LEGAL_REVIEW_PACK.md",
        "signoff": "P8_EXTERNAL_LEGAL_SIGNOFF.json",
        "supplemental": (),
    },
}

FILE_PATTERN = re.compile(r"(?m)^- File:\s*`([^`]+)`\s*$")


def canonical_bytes(path: Path) -> bytes:
    raw = path.read_bytes()
    return raw.replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(canonical_bytes(path)).hexdigest()


def normalise_relative_path(value: str) -> str:
    path = Path(value)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError(f"Unsafe review-scope path: {value}")
    return path.as_posix()


def scope_paths(root: Path, scope: str) -> list[str]:
    if scope not in SCOPES:
        raise ValueError(f"Unknown review scope: {scope}")

    config = SCOPES[scope]
    pack_relative = str(config["pack"])
    pack_path = root / pack_relative

    if not pack_path.exists():
        raise FileNotFoundError(f"Review pack missing: {pack_relative}")

    pack_text = pack_path.read_text(encoding="utf-8")
    listed = [normalise_relative_path(item) for item in FILE_PATTERN.findall(pack_text)]

    relatives = [
        normalise_relative_path(pack_relative),
        *[normalise_relative_path(str(item)) for item in config.get("supplemental", ())],
        *listed,
    ]

    unique = sorted(set(relatives))

    if not unique:
        raise ValueError(f"Review scope {scope} contains no files")

    missing = [relative for relative in unique if not (root / relative).is_file()]
    if missing:
        raise FileNotFoundError("Review-scope files missing: " + ", ".join(missing))

    return unique


def entries_for_scope(root: Path, scope: str) -> list[dict[str, str]]:
    return [
        {"path": relative, "sha256": sha256_file(root / relative)}
        for relative in scope_paths(root, scope)
    ]


def bundle_digest(entries: list[dict[str, str]]) -> str:
    canonical = json.dumps(
        sorted(entries, key=lambda item: item["path"]),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def create_snapshot(root: Path, scope: str) -> dict[str, Any]:
    entries = entries_for_scope(root, scope)
    return {
        "schemaVersion": SCHEMA_VERSION,
        "scope": SCOPES[scope]["scopeId"],
        "algorithm": ALGORITHM,
        "capturedAt": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "digest": bundle_digest(entries),
        "files": entries,
    }


def validate_snapshot(
    root: Path,
    snapshot: Any,
    scope: str,
) -> dict[str, Any]:
    scope_id = SCOPES[scope]["scopeId"]

    try:
        current_entries = entries_for_scope(root, scope)
    except (FileNotFoundError, ValueError) as exc:
        return {
            "valid": False,
            "status": "scope-error",
            "scope": scope_id,
            "algorithm": ALGORITHM,
            "error": str(exc),
            "changedFiles": [],
            "missingFiles": [],
            "unexpectedFiles": [],
        }

    current_map = {item["path"]: item["sha256"] for item in current_entries}
    current_digest = bundle_digest(current_entries)

    result: dict[str, Any] = {
        "valid": False,
        "status": "missing",
        "scope": scope_id,
        "algorithm": ALGORITHM,
        "recordedDigest": None,
        "currentDigest": current_digest,
        "aggregateDigestValid": False,
        "changedFiles": [],
        "missingFiles": [],
        "unexpectedFiles": [],
    }

    if not isinstance(snapshot, dict):
        return result

    result["recordedDigest"] = snapshot.get("digest")

    structure_valid = (
        snapshot.get("schemaVersion") == SCHEMA_VERSION
        and snapshot.get("scope") == scope_id
        and snapshot.get("algorithm") == ALGORITHM
        and isinstance(snapshot.get("files"), list)
        and isinstance(snapshot.get("digest"), str)
    )

    if not structure_valid:
        result["status"] = "invalid"
        return result

    recorded_entries: list[dict[str, str]] = []
    duplicate_paths: list[str] = []
    seen: set[str] = set()

    for item in snapshot["files"]:
        if (
            not isinstance(item, dict)
            or not isinstance(item.get("path"), str)
            or not isinstance(item.get("sha256"), str)
        ):
            result["status"] = "invalid"
            return result

        relative = normalise_relative_path(item["path"])
        if relative in seen:
            duplicate_paths.append(relative)
        seen.add(relative)
        recorded_entries.append({"path": relative, "sha256": item["sha256"]})

    if duplicate_paths:
        result["status"] = "invalid"
        result["duplicateFiles"] = sorted(set(duplicate_paths))
        return result

    recorded_map = {item["path"]: item["sha256"] for item in recorded_entries}

    expected_paths = set(current_map)
    recorded_paths = set(recorded_map)

    missing = sorted(expected_paths - recorded_paths)
    unexpected = sorted(recorded_paths - expected_paths)
    changed = sorted(
        relative
        for relative in expected_paths & recorded_paths
        if current_map[relative] != recorded_map[relative]
    )

    aggregate_valid = snapshot["digest"] == bundle_digest(recorded_entries)

    result.update(
        {
            "aggregateDigestValid": aggregate_valid,
            "changedFiles": changed,
            "missingFiles": missing,
            "unexpectedFiles": unexpected,
        }
    )

    valid = (
        aggregate_valid
        and not changed
        and not missing
        and not unexpected
        and snapshot["digest"] == current_digest
    )

    result["valid"] = valid
    result["status"] = (
        "valid" if valid else ("stale" if changed or missing or unexpected else "invalid")
    )
    return result


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def has_review_activity(record: dict[str, Any], scope: str) -> bool:
    if record.get("gateSatisfied") is True:
        return True

    for key in (
        "reviewDate",
        "finalRecommendation",
        "signatureOrElectronicAcknowledgement",
    ):
        value = record.get(key)
        if value is not None and str(value).strip():
            return True

    if scope == "clinical" and record.get("conceptDecisions"):
        return True

    if scope == "legal":
        legal_scope = record.get("scope", {})
        if any(value is True for value in legal_scope.values()):
            return True

    return False


def write_snapshot_to_signoff(root: Path, scope: str) -> dict[str, Any]:
    signoff_path = root / str(SCOPES[scope]["signoff"])
    signoff = load_json(signoff_path)

    if has_review_activity(signoff, scope):
        raise RuntimeError(
            "Refusing to refresh a snapshot after reviewer activity has begun. "
            "Return the review to an explicit pending state and obtain a new "
            "independent review before rebinding approval to changed material."
        )

    snapshot = create_snapshot(root, scope)
    signoff["reviewSnapshot"] = snapshot

    signoff_path.write_text(
        json.dumps(signoff, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return snapshot


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scope", choices=sorted(SCOPES), required=True)
    actions = parser.add_mutually_exclusive_group()
    actions.add_argument("--write-signoff", action="store_true")
    actions.add_argument("--check-signoff", action="store_true")
    args = parser.parse_args()

    if args.write_signoff:
        snapshot = write_snapshot_to_signoff(ROOT, args.scope)
        print(json.dumps(snapshot, indent=2))
        return 0

    if args.check_signoff:
        signoff_path = ROOT / str(SCOPES[args.scope]["signoff"])
        signoff = load_json(signoff_path)
        result = validate_snapshot(
            ROOT,
            signoff.get("reviewSnapshot"),
            args.scope,
        )
        print(json.dumps(result, indent=2))
        return 0 if result["valid"] else 1

    print(json.dumps(create_snapshot(ROOT, args.scope), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
