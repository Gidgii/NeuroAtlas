# Clinical Neuroscience Atlas

A mobile-first Progressive Web App for clinically useful neuroscience learning.

## Run locally

Serve the `app/` directory with any static HTTP server. Service workers do not run from `file://` URLs.

```bash
python -m http.server 8080 --directory app
```

Open `http://localhost:8080`.

## Interactive Anatomy runtime

Interactive Anatomy records declare the canonical `explorer` schema. The generic explorer resolves
selectable anatomy, input–connection–output stages, clinical overlays, overview reset, keyboard
controls, screen-reader announcements and reduced-motion behaviour from each structure's existing
clinical content. Repository validation tests are located in `tests/`.

The interface exposes a visual-scene control or generic explorer only when the corresponding runtime
model exists. Detail records without selectable anatomy render their educational content without an
empty explorer.

## Artwork readiness

Every curriculum concept declares one `artworkReadiness` value: `Placeholder`, `Functional`,
`Ready for Production`, `Premium` or `Locked`. Status meanings, current counts and promotion evidence
are recorded in `ARTWORK_READINESS_REPORT.json`. Artwork must not be promoted beyond `Functional`
without rendered clinical, responsive and accessibility review.

## Reproducible browser QA

The committed runtime harness exercises the rendered application in Chromium: startup, search, all
249 concept pages, live visual scenes, depth tabs, bookmarks, quiz/progress/review persistence,
reduced-motion explorer behaviour, mobile overflow and basic accessible-control contracts.

Install the optional browser-QA dependency and Chromium once:

```bash
pip install -e ".[runtime]"
python -m playwright install chromium
```

Run the production HTTP path locally:

```bash
python tools/runtime_qa.py --transport http
```

For locked-down environments that prohibit loopback navigation, the same application JavaScript and
JSON can be exercised in an in-memory Chromium document:

```bash
python tools/runtime_qa.py --transport injected
```

The harness writes `RUNTIME_QA_REPORT.json`. The injected transport validates application/UI logic but
does not claim service-worker or real-network coverage; the HTTP transport is the release gate for
those browser-loading behaviours.

## Validate

```bash
python launcher.py validate --no-update-state
pytest
ruff check .
ruff format --check .
```
