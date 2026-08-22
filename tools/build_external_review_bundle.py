#!/usr/bin/env python3
"""Build deterministic external-review hand-off bundles for NeuroAtlas."""

from __future__ import annotations

import argparse
import hashlib
import json
import zipfile
from pathlib import Path
from typing import Any

try:
    from reviewer_snapshot import (
        SCOPES,
        canonical_bytes,
        validate_snapshot,
    )
except ModuleNotFoundError:
    from tools.reviewer_snapshot import (
        SCOPES,
        canonical_bytes,
        validate_snapshot,
    )

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "external-review-bundles"

BUNDLE_FORMAT = "neuroatlas-external-review-bundle-v1"
ZIP_DATE = (1980, 1, 1, 0, 0, 0)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def normalised_text_bytes(text: str) -> bytes:
    return text.replace("\r\n", "\n").replace("\r", "\n").encode("utf-8")


def zip_info(name: str) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(name, date_time=ZIP_DATE)
    info.compress_type = zipfile.ZIP_DEFLATED
    info.create_system = 3
    info.external_attr = 0o100644 << 16
    return info


def reviewer_guide(scope: str, digest: str, signoff_path: str) -> str:
    if scope == "clinical":
        role = "independent clinical reviewer"
        review_pack = "P3_1_EXTERNAL_CLINICAL_REVIEW_PACK.md"
    else:
        role = "independent legal reviewer"
        review_pack = "P8_EXTERNAL_LEGAL_REVIEW_PACK.md"

    return f"""NEUROATLAS EXTERNAL REVIEW HAND-OFF

Review type: {scope}
Snapshot digest: {digest}
Reviewer role: {role}

START HERE
1. Read {review_pack}.
2. Review the supplied source material.
3. Complete {signoff_path}.
4. Do not alter reviewSnapshot in the sign-off record.
5. Return the completed sign-off record to the NeuroAtlas project owner.

FOR A RELEASE-APPROVING RETURN
- Set status to: approved-external-review
- Record reviewer name, qualification and professional credential.
- Record reviewDate as YYYY-MM-DD.
- Record a real signature or electronic acknowledgement.
- Set finalRecommendation to APPROVE or APPROVE WITH MINOR CHANGES.
- Set gateSatisfied to true only after the review is actually complete.
- Do not alter reviewSnapshot, sample IDs or other frozen review fields.

Clinical reviewers must complete all 25 concept decisions and all global
findings. Legal reviewers must complete every scope field and legal finding.

Software can verify structure and snapshot integrity. It cannot prove that a
reviewer is genuinely independent. The project owner must separately confirm
reviewer independence and suitability before importing the returned record.

IMPORTANT
Approval applies only to snapshot digest:

{digest}

If reviewed source material is changed after this review, the NeuroAtlas
release gate will mark the approval stale and require renewed review.

Internal engineering, automated testing and AI assistance do not constitute
the independent human review requested by this bundle.
"""


def build_manifest(
    scope: str,
    signoff: dict[str, Any],
    signoff_path: str,
) -> dict[str, Any]:
    snapshot = signoff["reviewSnapshot"]

    return {
        "bundleFormat": BUNDLE_FORMAT,
        "scope": snapshot["scope"],
        "snapshotAlgorithm": snapshot["algorithm"],
        "snapshotCapturedAt": snapshot["capturedAt"],
        "snapshotDigest": snapshot["digest"],
        "reviewSignoff": signoff_path,
        "reviewedFiles": snapshot["files"],
    }


def validate_source_snapshot(
    root: Path,
    scope: str,
    signoff: dict[str, Any],
) -> dict[str, Any]:
    result = validate_snapshot(
        root,
        signoff.get("reviewSnapshot"),
        scope,
    )

    if result.get("valid") is not True:
        raise RuntimeError(
            f"Refusing to package stale or invalid {scope} review material: {result.get('status')}"
        )

    return result


def expected_bundle_filename(scope: str, digest: str) -> str:
    return f"neuroatlas-{scope}-review-{digest[:12]}.zip"


def build_bundle(
    root: Path,
    scope: str,
    output_dir: Path,
) -> Path:
    config = SCOPES[scope]
    signoff_path = str(config["signoff"])
    signoff_file = root / signoff_path
    signoff = load_json(signoff_file)

    validate_source_snapshot(root, scope, signoff)

    snapshot = signoff["reviewSnapshot"]
    digest = snapshot["digest"]

    manifest = build_manifest(scope, signoff, signoff_path)
    manifest_bytes = normalised_text_bytes(
        json.dumps(
            manifest,
            indent=2,
            ensure_ascii=False,
            sort_keys=True,
        )
        + "\n"
    )

    guide_bytes = normalised_text_bytes(reviewer_guide(scope, digest, signoff_path))

    signoff_bytes = canonical_bytes(signoff_file)

    output_dir.mkdir(parents=True, exist_ok=True)

    bundle_path = output_dir / expected_bundle_filename(scope, digest)

    with zipfile.ZipFile(
        bundle_path,
        mode="w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=9,
    ) as archive:
        archive.writestr(
            zip_info("00_READ_ME_FIRST.txt"),
            guide_bytes,
        )

        archive.writestr(
            zip_info("00_BUNDLE_MANIFEST.json"),
            manifest_bytes,
        )

        for item in sorted(
            snapshot["files"],
            key=lambda entry: entry["path"],
        ):
            relative = item["path"]
            data = canonical_bytes(root / relative)

            actual_hash = sha256_bytes(data)
            if actual_hash != item["sha256"]:
                raise RuntimeError(f"Snapshot hash mismatch while packaging: {relative}")

            archive.writestr(
                zip_info(relative),
                data,
            )

        archive.writestr(
            zip_info(signoff_path),
            signoff_bytes,
        )

    return bundle_path


def verify_bundle(
    bundle_path: Path,
    root: Path,
    scope: str,
) -> dict[str, Any]:
    config = SCOPES[scope]
    signoff_path = str(config["signoff"])
    signoff = load_json(root / signoff_path)

    validate_source_snapshot(root, scope, signoff)

    snapshot = signoff["reviewSnapshot"]
    expected_files = {item["path"]: item["sha256"] for item in snapshot["files"]}

    with zipfile.ZipFile(bundle_path, "r") as archive:
        names = set(archive.namelist())

        required = {
            "00_READ_ME_FIRST.txt",
            "00_BUNDLE_MANIFEST.json",
            signoff_path,
            *expected_files.keys(),
        }

        missing = sorted(required - names)
        unexpected = sorted(names - required)

        hash_failures: list[str] = []

        for relative, expected_hash in expected_files.items():
            actual_hash = sha256_bytes(archive.read(relative))
            if actual_hash != expected_hash:
                hash_failures.append(relative)

        manifest = json.loads(archive.read("00_BUNDLE_MANIFEST.json").decode("utf-8"))

        manifest_valid = (
            manifest.get("bundleFormat") == BUNDLE_FORMAT
            and manifest.get("scope") == snapshot["scope"]
            and manifest.get("snapshotDigest") == snapshot["digest"]
            and manifest.get("reviewSignoff") == signoff_path
        )

    valid = not missing and not unexpected and not hash_failures and manifest_valid

    return {
        "valid": valid,
        "scope": scope,
        "bundle": str(bundle_path),
        "snapshotDigest": snapshot["digest"],
        "missingFiles": missing,
        "unexpectedFiles": unexpected,
        "hashFailures": hash_failures,
        "manifestValid": manifest_valid,
    }


def build_and_verify(
    root: Path,
    scope: str,
    output_dir: Path,
) -> dict[str, Any]:
    first = build_bundle(root, scope, output_dir)
    first_bytes = first.read_bytes()

    second = build_bundle(root, scope, output_dir)
    second_bytes = second.read_bytes()

    deterministic = first_bytes == second_bytes

    report = verify_bundle(first, root, scope)
    report["deterministic"] = deterministic
    report["bundleSha256"] = sha256_bytes(first_bytes)
    report["sizeBytes"] = len(first_bytes)
    report["valid"] = report["valid"] and deterministic

    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--scope",
        choices=("clinical", "legal", "all"),
        default="all",
    )
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT),
    )
    parser.add_argument(
        "--write-report",
    )
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    if not output_dir.is_absolute():
        output_dir = ROOT / output_dir

    scopes = ("clinical", "legal") if args.scope == "all" else (args.scope,)

    reports = [build_and_verify(ROOT, scope, output_dir) for scope in scopes]

    result = {
        "status": ("PASS" if all(report["valid"] for report in reports) else "FAIL"),
        "bundleFormat": BUNDLE_FORMAT,
        "bundles": reports,
    }

    if args.write_report:
        report_path = Path(args.write_report)
        if not report_path.is_absolute():
            report_path = ROOT / report_path

        report_path.write_text(
            json.dumps(
                result,
                indent=2,
                ensure_ascii=False,
            )
            + "\n",
            encoding="utf-8",
        )

    print(json.dumps(result, indent=2))

    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
