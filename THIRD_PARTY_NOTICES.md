# NeuroAtlas Third-Party Notices

## Scope

This inventory records third-party software identified in the NeuroAtlas repository as of 21 August 2026.

The shipped NeuroAtlas PWA is a static browser application. The Python packages below support repository tooling, validation, development, testing or browser QA and are not identified as bundled JavaScript/runtime libraries within the released PWA.

Third-party packages remain subject to their own licence terms.

| Component | Role | Licence identified |
|---|---|---|
| setuptools | Build tooling | MIT |
| wheel | Build tooling | MIT |
| pydantic | Repository tooling | MIT |
| rich | Repository tooling | MIT |
| typer | Repository tooling | MIT |
| python-dotenv | Repository tooling | BSD-3-Clause |
| orjson | Repository tooling | MPL-2.0 AND (Apache-2.0 OR MIT) |
| jsonschema | Repository tooling | MIT |
| packaging | Repository tooling | Apache and BSD licence terms |
| pytest | Development/testing | MIT |
| pytest-cov | Development/testing | MIT |
| ruff | Development/testing | MIT |
| playwright | Runtime/browser QA tooling | Apache-2.0 |

## Upstream licence evidence

Licence information was obtained from installed package metadata where available and checked against upstream project metadata or licence files.

Notably:

- setuptools upstream licence file contains the MIT licence terms.
- wheel upstream `LICENSE.txt` identifies the MIT Licence.
- installed distributions contained their applicable licence or notice files for the remaining resolved dependencies.

## Application assets

The repository contains:

- 249 SVG illustrations;
- 2 PNG application icons.

Repository history records these assets as additions within the NeuroAtlas project repository under the Gidgii GitHub identity.

Internal scans did not identify:

- externally hosted runtime fonts;
- CDN-hosted JavaScript libraries;
- third-party browser imports;
- embedded external image URLs;
- obvious reproduced journal figures or tables;
- bundled third-party font files.

This repository history and scan provide provenance evidence, but do not by themselves constitute independent proof of copyright ownership.

Development has included AI-assisted generation and editing. Rights in AI-assisted material may depend on the degree of protectable human authorship and applicable law.

## Academic and clinical references

Scientific references remain owned by their respective publishers and authors.

NeuroAtlas policy is to store citations, identifiers, summaries and links rather than reproduce copyrighted source text or figures beyond lawful use.

## Status

Internal dependency and asset-provenance inventory: COMPLETE.

Independent copyright/legal review: NOT COMPLETED.

This document is an internal release-governance record and is not a legal-clearance certificate.
