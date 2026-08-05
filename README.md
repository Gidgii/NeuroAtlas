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

## Validate

```bash
python launcher.py validate --no-update-state
pytest
ruff check .
ruff format --check .
```
