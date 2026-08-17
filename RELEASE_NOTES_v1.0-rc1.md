# NeuroAtlas v1.0-rc1

First release candidate for NeuroAtlas v1.0.

## Release status
- P6/P7 complete and regression-tested
- P8 release-candidate hardening complete
- Browser QA passed on mobile, tablet and desktop
- Runtime QA passed
- Repository validation passed
- GitHub Actions Atlas QA passed

## QA results
- P6/P7 regression: 26/26 passed
- Full pytest suite: 51/51 passed
- P8 release audit: PASS
- Runtime QA: 28/28 passed
- Browser QA: PASS
- Repository validation: PASS

## Release commit
abbe760 — Complete P8 release candidate hardening

## Important runtime/cache behaviour
The service worker precaches:
- p8-release.css
- p8-release.js
- legal/third-party-notices.html

The following remain runtime-fetched/runtime-cached and are not statically precached:
- data/release-manifest.json
- data/assessment-bank.json

## P8 UI hardening
Beta Feedback now waits for the dynamically-created release footer using a bounded MutationObserver.
