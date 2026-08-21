# NeuroAtlas External Legal Review Pack

## Purpose

This pack supports independent legal and licensing review before any public v1.0 release claim.

Internal engineering, governance work, AI assistance, repository audits and automated tests do not constitute independent legal advice or legal clearance.

## Required reviewer scope

Please review the current release for:

1. Public disclaimer and limitation-of-use wording.
2. The four-part acknowledgement design and the current local acceptance-record model.
3. Copyright notices and the stated provenance boundary for repository assets.
4. Third-party dependency and notice disclosures.
5. The privacy position of the current local-only release.
6. Any material legal issue that should block public v1.0.

The reviewer may request additional repository material if required.

## Review snapshot integrity

The review is bound to the `reviewSnapshot` stored in `P8_EXTERNAL_LEGAL_SIGNOFF.json`.

The snapshot uses SHA-256 hashes over canonical LF-normalised text. Approval applies only to the exact files represented by that digest. If any reviewed file changes after the snapshot is created, the public-v1 gate must treat the sign-off as stale until the changed material is independently reviewed again.

## Files in the legal review snapshot

- File: `COPYRIGHT.md`
- File: `THIRD_PARTY_NOTICES.md`
- File: `P8_LEGAL_LICENSING_GOVERNANCE_REPORT.json`
- File: `P8_ACKNOWLEDGEMENT_GATE_REPORT.json`
- File: `app/legal/disclaimer.html`
- File: `app/legal/privacy.html`
- File: `app/legal/release.html`
- File: `app/legal/third-party-notices.html`
- File: `app/acknowledgement-gate.js`
- File: `app/acknowledgement-gate.css`
- File: `app/index.html`
- File: `app/data/release-manifest.json`
- File: `requirements.txt`
- File: `pyproject.toml`

## Required outcome

Record the outcome in `P8_EXTERNAL_LEGAL_SIGNOFF.json`.

A gate-satisfying review requires:

- an appropriately qualified independent reviewer;
- completion of every required scope item;
- no unresolved material legal concern;
- an approved final recommendation;
- reviewer signature or electronic acknowledgement;
- a valid, current review snapshot.

Permitted approval recommendations are:

- APPROVE
- APPROVE WITH MINOR CHANGES

Any substantive required change must be implemented and independently re-reviewed before the public-v1 legal gate is satisfied.
