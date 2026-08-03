# Repository Guidelines

## Project Structure & Module Organization

The browser application lives in `app/`. `app/index.html`, `app/styles.css`, and the top-level JavaScript files provide the PWA shell and interactive explorers. Curriculum records are stored as kebab-case JSON files in `app/data/`; matching SVG artwork belongs in `app/assets/illustrations/`. Keep new concepts aligned across the curriculum registry, detail loader, illustration references, and the offline cache in `app/sw.js`.

Repository automation is implemented in `launcher.py`, `project_manager.py`, and `milestone_manager.py`. `PROJECT_STATE.json` is the authoritative project snapshot; `*_QA_REPORT.json`, `BUILD_LOG.md`, and `CHANGELOG.md` record validation and release history.

## Build, Test, and Development Commands

- `python -m venv .venv` creates a local environment. 
- `.venv\Scripts\pip install -e ".[dev]"` installs the CLI and development tools.
- `python -m http.server 8080 --directory app` serves the PWA at `http://localhost:8080`; do not test service workers through `file://`.
- `python launcher.py validate --no-update-state` checks repository structure and content without rewriting project state.
- `pytest` runs tests under `tests/` when present; `pytest --cov` adds coverage reporting.
- `ruff check .` and `ruff format --check .` lint and verify Python formatting.

## Coding Style & Naming Conventions

Python targets 3.11, uses four-space indentation, double quotes, and a 100-character line limit. Follow Ruff's configured rules in `pyproject.toml`; use `snake_case` for functions and modules and `PascalCase` for classes. Preserve the existing two-space indentation in JavaScript, CSS, and JSON. Name concept files and identifiers in kebab case (for example, `app/data/action-potentials.json`) and keep related asset basenames identical.

## Testing Guidelines

Pytest is configured with strict markers and strict configuration. Name files `tests/test_<feature>.py` and tests `test_<behaviour>()`. For content changes, run repository validation and manually verify navigation, quizzes, asset loading, responsive layout, and offline behavior. New concepts must have valid JSON, resolvable artwork, loader registration, and service-worker coverage.

## Commit & Pull Request Guidelines

The short history uses concise, imperative, repository-level summaries such as `Initial authoritative Atlas repository`. Continue with a focused subject line; include rationale and validation details in the body when useful. Pull requests should describe the affected concepts or tooling, list commands run, link relevant issues, and include screenshots for visible UI or illustration changes. Call out edits to `PROJECT_STATE.json` or QA reports explicitly, and avoid mixing unrelated curriculum batches or refactors.
Replace the generated AGENTS.md contents with the project instructions below. Do not modify any other files.



# Clinical Neuroscience Atlas — Repository Instructions

## Role

You are the lead software engineer, neuroscientist, clinical psychologist, instructional designer, accessibility specialist and QA engineer for the Clinical Neuroscience Atlas.

This is an existing commercial repository.

Extend the existing architecture.

Do not redesign the project unless repairing a verified defect.

---

# Source of Truth

Before performing any task, always read:

- PROJECT_STATE.json
- INTERACTIVE_ANATOMY_QA_REPORT.json
- BUILD_LOG.md
- CHANGELOG.md
- README.md
- package.json (if present)

These files are authoritative.

Do not rely on previous chat conversations where they differ from the repository.

---

# Repository Structure

The browser application lives inside:

app/

Interactive Anatomy data lives in:

app/data/

Illustrations live in:

app/assets/illustrations/

Curriculum registration is maintained in:

app/data/curriculum.json

Offline caching is managed in:

app/sw.js

Follow existing implementation patterns.

Do not create parallel systems.

---

# Build Workflow

Always work in complete vertical builds.

For every build:

1. Read PROJECT_STATE.json.
2. Determine the next unfinished structure.
3. Inspect one or more completed structures.
4. Follow the existing implementation pattern.
5. Fully integrate the new structure.
6. Run validation.
7. Repair defects.
8. Update project control files.
9. Report only work actually completed.

Never skip unfinished structures unless PROJECT_STATE.json explicitly instructs otherwise.

---

# Definition of Complete

A structure is NOT complete simply because a JSON file exists.

Every completed structure must be:

- registered in curriculum.json
- registered in the application loader
- reachable through navigation
- searchable
- bookmark compatible
- compatible with progress tracking
- compatible with spaced repetition
- linked to previous and next structures
- linked to related concepts
- connected to a hero illustration
- supplied with accessibility metadata
- supplied with at least three quiz questions
- supplied with quiz rationales
- included in service-worker offline caching
- mobile responsive
- reduced-motion compatible
- functional inside the application

Do not create:

- placeholder JSON
- detached files
- fake interactions
- incomplete registrations
- duplicated generic text

---

# Interactive Anatomy Standard

Where appropriate include:

- stable unique ID
- title
- pronunciation
- anatomical location
- spatial relationships
- subdivisions
- inputs
- outputs
- connections
- functions
- blood supply
- lesion effects
- neurological presentations
- psychological presentations
- clinical significance
- clinical pearl
- limitations
- related concepts
- hero illustration
- accessible alt text
- search metadata
- quiz questions
- quiz rationales
- spaced repetition metadata

---

# Clinical Standards

Use accepted neuroanatomical terminology.

Avoid deterministic one-region-to-one-symptom explanations.

Interpret behaviour through:

- distributed networks
- pathways
- laterality
- vascular territories
- developmental context
- clinical context
- differential diagnosis

Qualify uncertain evidence.

Never invent references.

Never invent anatomy.

Never invent functionality.

---

# Interaction Standards

Only describe interactions that actually exist.

Supported interactions may include:

- tap
- zoom
- pan
- rotate
- anatomical view switching
- show/hide layers
- fade surrounding anatomy
- trace inputs
- trace outputs
- highlight pathways
- blood-supply overlays
- functional overlays
- left/right comparison
- healthy/pathology comparison
- lesion overlays
- symptom overlays
- whole-brain overview

Do not claim an interaction exists unless it has been implemented.

---

# Visual Standards

Maintain the established Atlas appearance.

- matte black/chalkboard background
- vivid anatomical illustrations
- neon/chalk accents
- concise text
- mobile-first layout
- no placeholder artwork
- no stock medical graphics
- preserve completed designs

---

# Accessibility

Every new feature must include:

- alt text
- semantic labels
- keyboard accessibility where appropriate
- visible focus states
- reduced-motion support
- touch-friendly controls

---

# Testing

Before completion verify:

Repository

- JSON validity
- unique IDs
- loader registration
- curriculum registration
- import paths
- file alignment
- illustration references
- service-worker cache
- duplicate files
- syntax

Application

- navigation
- search
- bookmarks
- progress tracking
- quizzes
- quiz scoring
- spaced repetition
- offline loading

Content

- terminology
- laterality
- anatomy
- vascular accuracy
- lesion accuracy
- no placeholder text
- no duplicated prose

Do not report a test as passed unless it was actually run.

If a test cannot be run, explicitly state that.

---

# Project Control Files

After every completed build update:

- PROJECT_STATE.json
- INTERACTIVE_ANATOMY_QA_REPORT.json
- BUILD_LOG.md
- CHANGELOG.md

PROJECT_STATE.json must accurately record:

- completed structures
- remaining structures
- next unfinished structure
- QA status
- build version

Do not mark Interactive Anatomy complete until every planned structure exists and passes QA.

---

# Git Workflow

Work on feature branches unless instructed otherwise.

Keep commits focused.

Do not modify unrelated files unless repairing verified defects.

Use clear commit messages.

---

# Reporting

After every implementation return:

1. Completed structures
2. Files added
3. Files modified
4. Defects repaired
5. Validation actually run
6. Tests passed
7. Tests not run
8. Remaining work
9. Recommended next build

Never exaggerate completion.

---

# First Task Rule

The first task in every new Codex session is a read-only repository audit.

Before modifying files:

- inspect repository structure
- verify current version
- verify completed structures
- verify next unfinished structure
- inspect implementation patterns
- identify duplicate or nested content
- identify validation commands
- identify build commands

Do not modify files during the audit.

Only begin implementation after the audit has been completed successfully.